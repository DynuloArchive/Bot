"""Profiles for Disco"""
import discord
import bot

class Profiles(bot.Extension):
    """Profiles for Disco"""

    @bot.argument("[member+]", discord.Member, "author")
    @bot.command()
    async def avatar(ctx, message):
        """Prints out a users discord avatar"""
        embed = discord.Embed(
            color=ctx.args.member.color
        )
        embed.set_author(
            name=ctx.args.member.display_name,
            url=ctx.args.member.avatar_url
        )
        embed.set_image(url=ctx.args.member.avatar_url)
        await message.channel.send(embed=embed)

    @bot.argument("[member+]", discord.Member, "author")
    @bot.command()
    async def card(ctx, message):
        """Display a card with information about a member"""
        embed = discord.Embed(
            title=ctx.args.member.display_name,
            color=ctx.args.member.colour
        )
        embed.add_field(name="Joined on", value=ctx.args.member.joined_at.strftime("%B %d, %Y"))
        embed.set_thumbnail(url=ctx.args.member.avatar_url)
        await message.channel.send(embed=embed)

    @bot.argument("role+", discord.Role)
    @bot.command()
    async def color(ctx, message):
        """Obtain the color of a role on the server"""
        embed = discord.Embed(
            title=ctx.args.role.name,
            color=ctx.args.role.colour
        )
        embed.add_field(name="RGB", value="{0.r}, {0.g}, {0.b}".format(ctx.args.role.color))
        embed.add_field(name="Hex", value=str(ctx.args.role.color))
        await message.channel.send(embed=embed)
