
from app.common.constants import UserActivity
from app.common.database import DBActivity

import config

def format_ranks_gained(activity: DBActivity) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'{config.OSU_BASEURL}/u/{activity.user_id}'
    )

    return (
        f'{user_link} has risen {activity.data["ranks_gained"]} '
        f'rank{"s" if activity.data["ranks_gained"] != 1 else ""}, '
        f'now placed #{activity.data["rank"]} overall in {activity.data["mode"]}.'
    )

def format_number_one(activity: DBActivity) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'{config.OSU_BASEURL}/u/{activity.user_id}'
    )

    return (
        f'{user_link} has taken the lead as the top-ranked '
        f'{activity.data["mode"]} player.'
    )

def format_leaderboard_rank(activity: DBActivity) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'{config.OSU_BASEURL}/u/{activity.user_id}'
    )
    beatmap_link = format_chat_link(
        activity.data['beatmap'],
        f'{config.OSU_BASEURL}/b/{activity.data["beatmap_id"]}'
    )
    data = dict(activity.data)

    return "".join([
        f'{user_link} achieved rank #{data["beatmap_rank"]} on {beatmap_link} ',
        (
            f'with {data["mods"]} '
            if data.get("mods") else ""
        ),
        f'<{data["mode"]}>',
        (
            f' ({data["pp"]}pp)'
            if data.get("pp") else ""
        )
    ])

def format_lost_first_place(activity: DBActivity) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'{config.OSU_BASEURL}/u/{activity.user_id}'
    )
    beatmap_link = format_chat_link(
        activity.data['beatmap'],
        f'{config.OSU_BASEURL}/b/{activity.data["beatmap_id"]}'
    )

    return f'{user_link} has lost first place on {beatmap_link} <{activity.data["mode"]}>'

def format_pp_record(activity: DBActivity) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'{config.OSU_BASEURL}/u/{activity.user_id}'
    )
    beatmap_link = format_chat_link(
        activity.data['beatmap'],
        f'{config.OSU_BASEURL}/b/{activity.data["beatmap_id"]}'
    )

    return (
        f'{user_link} has set the new pp record on {beatmap_link} with'
        f' {activity.data["pp"]}pp <{activity.data["mode"]}>'
    )

def format_top_play(activity: DBActivity) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'{config.OSU_BASEURL}/u/{activity.user_id}'
    )
    beatmap_link = format_chat_link(
        activity.data['beatmap'],
        f'{config.OSU_BASEURL}/b/{activity.data["beatmap_id"]}'
    )

    return (
        f'{user_link} got a new top play on {beatmap_link} with '
        f'{activity.data["pp"]}pp <{activity.data["mode"]}>'
    )

def format_achievement(activity: DBActivity) -> str:
    user_link = format_chat_link(
        activity.data['username'],
        f'{config.OSU_BASEURL}/u/{activity.user_id}'
    )

    return f'{user_link} unlocked an achievement: {activity.data["achievement"]}'

def format_chat_link(key: str, value: str) -> str:
    key = key.replace('(', '&#40;').replace(')', '&#41;') \
             .replace('[', '&#91;').replace(']', '&#93;')

    value = value.replace('(', '&#40;').replace(')', '&#41;') \
                 .replace('[', '&#91;').replace(']', '&#93;')

    return f'[{value} {key}]'

formatters = {
    UserActivity.RanksGained.value: format_ranks_gained,
    UserActivity.NumberOne.value: format_number_one,
    UserActivity.BeatmapLeaderboardRank.value: format_leaderboard_rank,
    UserActivity.LostFirstPlace.value: format_lost_first_place,
    UserActivity.PPRecord.value: format_pp_record,
    UserActivity.TopPlay.value: format_top_play,
    UserActivity.AchievementUnlocked.value: format_achievement
}
