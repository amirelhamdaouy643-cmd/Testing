import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

# الرتبة المسموح لها باستخدام /say
ALLOWED_ROLE_ID = 1538295248550371339


class SayBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()


bot = SayBot()


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"🆔 Bot ID: {bot.user.id}")


@bot.tree.command(name="say", description="إرسال رسالة باسم عضو محدد")
@app_commands.describe(
    member="العضو الذي سيظهر اسمه وصورته",
    message="الرسالة التي تريد إرسالها",
    image="هل تريد إرفاق صورة؟",
    attachment="الصورة التي تريد إرسالها"
)
@app_commands.choices(
    image=[
        app_commands.Choice(name="Yes", value="yes"),
        app_commands.Choice(name="No", value="no")
    ]
)
async def say(
    interaction: discord.Interaction,
    member: discord.Member,
    message: str,
    image: app_commands.Choice[str],
    attachment: discord.Attachment | None = None
):
    # التحقق من الرتبة
    role = interaction.guild.get_role(ALLOWED_ROLE_ID)

    if role is None or role not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ ما عندك الرتبة المطلوبة لاستخدام هذا الأمر.",
            ephemeral=True
        )
        return

    # التحقق من الصورة
    if image.value == "yes" and attachment is None:
        await interaction.response.send_message(
            "❌ اخترت `Yes`، لازم ترفق صورة.",
            ephemeral=True
        )
        return

    if image.value == "no" and attachment is not None:
        await interaction.response.send_message(
            "❌ اخترت `No`، لا ترفق صورة.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        # البحث عن Webhook موجود للبوت
        webhooks = await interaction.channel.webhooks()
        webhook = discord.utils.get(webhooks, name="SayBot")

        # إنشاء Webhook إذا لم يكن موجودًا
        if webhook is None:
            webhook = await interaction.channel.create_webhook(
                name="SayBot",
                reason="Used for /say command"
            )

        # إرسال الرسالة باسم وصورة العضو
        await webhook.send(
            content=message,
            username=member.display_name,
            avatar_url=member.display_avatar.url,
            file=await attachment.to_file() if attachment else discord.utils.MISSING,
            wait=False
        )

        await interaction.followup.send(
            "✅ تم إرسال الرسالة.",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.followup.send(
            "❌ البوت يحتاج صلاحية `Manage Webhooks` في هذه القناة.",
            ephemeral=True
        )

    except Exception as e:
        print(f"ERROR: {e}")

        await interaction.followup.send(
            "❌ حدث خطأ أثناء إرسال الرسالة.",
            ephemeral=True
        )


bot.run(TOKEN)