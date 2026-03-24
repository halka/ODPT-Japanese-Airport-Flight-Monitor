#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import threading
from typing import List, Dict, Any

import discord
from discord import app_commands

import watch_list

_log = logging.getLogger(__name__)

intents = discord.Intents.default()
_client = discord.Client(intents=intents)
_tree = app_commands.CommandTree(_client)

# Exposed so discord_notifier can send via the bot
client = _client
_ready = threading.Event()


@_tree.command(name="watch", description="指定フライトを監視リストに追加")
@app_commands.describe(flight="フライト番号 (例: JL584)")
async def _watch(interaction: discord.Interaction, flight: str) -> None:
    fn = flight.strip().upper()
    if watch_list.add(fn):
        await interaction.response.send_message(f"`{fn}` を監視リストに追加しました。")
    else:
        await interaction.response.send_message(f"`{fn}` はすでに監視リストにあります。")


@_tree.command(name="unwatch", description="指定フライトを監視リストから削除")
@app_commands.describe(flight="フライト番号 (例: JL584)")
async def _unwatch(interaction: discord.Interaction, flight: str) -> None:
    fn = flight.strip().upper()
    if watch_list.remove(fn):
        await interaction.response.send_message(f"`{fn}` を監視リストから削除しました。")
    else:
        await interaction.response.send_message(f"`{fn}` は監視リストにありません。")


@_tree.command(name="watchlist", description="監視中のフライト一覧を表示")
async def _watchlist(interaction: discord.Interaction) -> None:
    flights = watch_list.get()
    if not flights:
        await interaction.response.send_message("監視リストは空です。全フライトを通知中。")
    else:
        await interaction.response.send_message(
            "監視中のフライト: " + ", ".join(f"`{f}`" for f in sorted(flights))
        )


@_tree.command(name="help", description="使用可能なコマンド一覧を表示")
async def _help(interaction: discord.Interaction) -> None:
    embed = discord.Embed(
        title="Airport Monitor — コマンド一覧",
        color=0x3498DB,
    )
    embed.add_field(
        name="`/watch <便名>`",
        value="指定フライトを監視リストに追加します。\n例: `/watch JL584`",
        inline=False,
    )
    embed.add_field(
        name="`/unwatch <便名>`",
        value="指定フライトを監視リストから削除します。\n例: `/unwatch JL584`",
        inline=False,
    )
    embed.add_field(
        name="`/watchlist`",
        value="現在の監視リストを表示します。\nリストが空の場合は全フライトを通知します。",
        inline=False,
    )
    embed.add_field(
        name="`/help`",
        value="このヘルプを表示します。",
        inline=False,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@_client.event
async def on_ready() -> None:
    await _tree.sync()
    _ready.set()
    _log.info("Discord bot ready: %s", _client.user)


async def _send_embeds(channel_id: int, embeds: List[Dict[str, Any]]) -> None:
    ch = _client.get_channel(channel_id) or await _client.fetch_channel(channel_id)
    for embed_dict in embeds:
        await ch.send(embed=discord.Embed.from_dict(embed_dict))


def post_embeds_sync(channel_id: int, embeds: List[Dict[str, Any]], timeout: float = 15.0) -> None:
    """Send embeds via the bot from a non-async (main) thread."""
    _ready.wait(timeout=timeout)
    future = asyncio.run_coroutine_threadsafe(_send_embeds(channel_id, embeds), _client.loop)
    future.result(timeout=timeout)


def run_bot(token: str) -> None:
    """Blocking call — run in a dedicated daemon thread."""
    _client.run(token, log_handler=None)
