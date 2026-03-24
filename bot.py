#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import discord
from discord import app_commands

import watch_list

_log = logging.getLogger(__name__)

intents = discord.Intents.default()
_client = discord.Client(intents=intents)
_tree = app_commands.CommandTree(_client)


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


@_client.event
async def on_ready() -> None:
    await _tree.sync()
    _log.info("Discord bot ready: %s", _client.user)


def run_bot(token: str) -> None:
    """Blocking call — run in a dedicated daemon thread."""
    _client.run(token, log_handler=None)
