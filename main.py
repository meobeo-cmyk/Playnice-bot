import discord
from discord.ext import commands
import asyncio
import os
import logging
from datetime import datetime, timedelta
from config import Config
from moderation import ModerationService
from database import ViolationDatabase
from utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class ModerationBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.moderation_service = ModerationService()
        self.violation_db = ViolationDatabase()
        
    async def on_ready(self):
        logger.info(f'{self.user} đã đăng nhập và sẵn sàng!')
        try:
            synced = await self.tree.sync()
            logger.info(f'Đã đồng bộ {len(synced)} slash command(s)')
        except Exception as e:
            logger.error(f'Lỗi khi đồng bộ commands: {e}')
    
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Check if user has admin permissions
        if message.author.guild_permissions.administrator:
            return
        
        try:
            # Check for violations
            violation_result = await self.moderation_service.check_message(message.content)
            
            if violation_result['is_violation']:
                await self.handle_violation(message, violation_result)
            
            # Check for Discord invite links
            if self.moderation_service.has_discord_invite(message.content):
                await self.handle_discord_invite(message)
                
        except Exception as e:
            logger.error(f'Lỗi khi kiểm tra tin nhắn: {e}')
    
    async def handle_violation(self, message, violation_result):
        """Handle message violation by deleting and muting user"""
        try:
            # Delete the message
            await message.delete()
            
            # Mute the user for 10 minutes
            mute_duration = timedelta(minutes=10)
            await message.author.timeout(mute_duration, reason=f"Vi phạm: {violation_result['violation_type']}")
            
            # Log the violation
            self.violation_db.add_violation(
                user_id=message.author.id,
                username=str(message.author),
                violation_type=violation_result['violation_type'],
                message_content=message.content,
                channel_id=message.channel.id,
                guild_id=message.guild.id
            )
            
            # Send notification to user
            try:
                embed = discord.Embed(
                    title="⚠️ Cảnh báo vi phạm",
                    description=f"Tin nhắn của bạn đã bị xóa do vi phạm quy định: **{violation_result['violation_type']}**",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(
                    name="Thời gian mute",
                    value="10 phút",
                    inline=True
                )
                embed.add_field(
                    name="Lý do",
                    value=violation_result.get('reason', 'Nội dung không phù hợp'),
                    inline=False
                )
                await message.author.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Không thể gửi DM cho {message.author}")
            
            logger.info(f"Đã xử lý vi phạm từ {message.author} trong {message.guild.name}")
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý vi phạm: {e}")
    
    async def handle_discord_invite(self, message):
        """Handle Discord invite links"""
        try:
            # Delete the message
            await message.delete()
            
            # Mute user for 5 minutes
            mute_duration = timedelta(minutes=5)
            await message.author.timeout(mute_duration, reason="Chia sẻ link Discord không được phép")
            
            # Log the violation
            self.violation_db.add_violation(
                user_id=message.author.id,
                username=str(message.author),
                violation_type="Discord Invite Link",
                message_content=message.content,
                channel_id=message.channel.id,
                guild_id=message.guild.id
            )
            
            # Send notification
            try:
                embed = discord.Embed(
                    title="🔗 Link không được phép",
                    description="Tin nhắn chứa link Discord invite đã bị xóa",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow()
                )
                await message.author.send(embed=embed)
            except discord.Forbidden:
                pass
                
            logger.info(f"Đã xóa Discord invite từ {message.author}")
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý Discord invite: {e}")

# Create bot instance
bot = ModerationBot()

@bot.tree.command(name="report", description="Xem báo cáo vi phạm trong 1 tuần qua (chỉ dành cho admin)")
async def report_command(interaction: discord.Interaction):
    # Check if user is admin
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        # Get violations from the past week
        violations = bot.violation_db.get_violations_last_week(interaction.guild.id)
        
        if not violations:
            embed = discord.Embed(
                title="📊 Báo cáo vi phạm (7 ngày qua)",
                description="Không có vi phạm nào trong tuần qua.",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create report embed
        embed = discord.Embed(
            title="📊 Báo cáo vi phạm (7 ngày qua)",
            description=f"Tổng cộng: **{len(violations)}** vi phạm",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        # Group violations by type
        violation_types = {}
        user_violations = {}
        
        for violation in violations:
            v_type = violation['violation_type']
            user_id = violation['user_id']
            username = violation['username']
            
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
            
            if user_id not in user_violations:
                user_violations[user_id] = {'username': username, 'count': 0}
            user_violations[user_id]['count'] += 1
        
        # Add violation types field
        types_text = '\n'.join([f"• {vtype}: {count}" for vtype, count in violation_types.items()])
        embed.add_field(
            name="📋 Loại vi phạm",
            value=types_text if types_text else "Không có",
            inline=True
        )
        
        # Add top violators field
        top_violators = sorted(user_violations.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        violators_text = '\n'.join([
            f"• {data['username']}: {data['count']} lần"
            for user_id, data in top_violators
        ])
        embed.add_field(
            name="👥 Top vi phạm",
            value=violators_text if violators_text else "Không có",
            inline=True
        )
        
        embed.set_footer(text="Dữ liệu từ 7 ngày qua")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Lỗi khi tạo báo cáo: {e}")
        await interaction.response.send_message("❌ Có lỗi xảy ra khi tạo báo cáo!", ephemeral=True)

@bot.tree.command(name="clear_violations", description="Xóa tất cả dữ liệu vi phạm (chỉ dành cho admin)")
async def clear_violations_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        bot.violation_db.clear_violations(interaction.guild.id)
        embed = discord.Embed(
            title="🗑️ Đã xóa dữ liệu",
            description="Tất cả dữ liệu vi phạm đã được xóa.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        logger.error(f"Lỗi khi xóa violations: {e}")
        await interaction.response.send_message("❌ Có lỗi xảy ra!", ephemeral=True)

if __name__ == "__main__":
    # Get bot token from environment
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN không được tìm thấy trong environment variables!")
        exit(1)
    
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"Lỗi khi chạy bot: {e}")
