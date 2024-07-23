from __future__ import annotations
from discord import ui
from pathlib import Path
from typing import Any, Optional, Union
from .model import WeatherResult

import discord
import re


class WeatherPages(ui.View):
    def __init__(
        self,
        entries : WeatherResult,
        *,
        author : Optional[Union[discord.Member, discord.User]] = None,
        ephemeral : bool = False
    ):
        if not self.check_invaild():
            raise ValueError('ephemeral과 author 둘 다 None일 수 없습니다.')
        
        super().__init__()
        self.entries = entries
        self.message : Optional[discord.InteractionMessage] = None
        self.author = author
        self.ephemeral = ephemeral
        self.clear_items()
        self.set_init()
    
    def check_invaild(self):
        if not self.ephemeral and not self.author:
            return False
        return True

    def set_init(self):
        # 제일 빠른 날짜이면서 제일 빠른 시간으로!
        weathers = self.entries.weather
        dates = [i.date for i in weathers]
        date = min(dates)
        time_and_wather = [j for i in weathers for j in i.time_weather if i.date == date]
        times = [i.time for i in time_and_wather]
        
        if dates and len(dates) > 1:        
            for num, _date in enumerate(dates):
                button = WeatherButton(_date)
                if num == 0:
                    button.style = discord.ButtonStyle.primary
                self.add_item(button)
        
        if len(times) > 1:
            select = TimeSelect(date=date, times=times)
            select.fill_options()
            self.add_item(select) 
        
        self.embed = discord.Embed(color=discord.Colour.blurple())
        self.embed.set_author(text='출처 - 대한민국 공식 전자정부 누리집', url='https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15084084')
        self.embed, self.file = self.try_edit_embed_message(custom_id=date)
    
    def search(self, custom_id : str, *, hour : Optional[str] = None, get_times : bool = False):
        """ 날짜가 주어져 있으며, 시간이 주어져 있든 주어져있지 않든 날씨를 찾습니다.
        단, 시간이 주어져 있지 않으면, 해당 날짜에서 가장 빠른 날짜의 날씨를 반환합니다."""
    
        weather = self.entries.weather
        times = [j.time for i in weather for j in i.time_weather if i.date == custom_id]
        if get_times:
            return times
        
        if hour and hour in times:
            time = hour
        else:
            time = min(times)
        
        for i in weather:
            for j in i.time_weather:
                if i.date == custom_id and j.time == time:
                    # 날짜, 시간, 날씨를 튜플로 반환
                    date = "%s년 %s월 %s일" % (custom_id[2:4], custom_id[4:6], custom_id[6:])
                    time = "## %s시" % (time[:2])
                    return date, time, j.weather       
        
    def try_edit_embed_message(
        self, 
        *, 
        custom_id : str,
        hour : Optional[str] = None
    ):
        date, time, weather = self.search(custom_id, hour=hour)
        self.embed.title = f"{self.entries.city_name}\n{date} 날씨"
        self.embed.description = time
        self.embed = self.embed.clear_fields()
        
        for name, value in weather.items():
            if name == 'filename':
                continue
            self.embed.add_field(name=name, value=value)
        
        file = weather['filename']
        path = Path(__file__).parent / 'asset/img' / f'{file}.png'
        self.file = discord.File(path, filename='weather.png')
        self.embed.set_thumbnail(url="attachment://weather.png")
        return self.embed, self.file       
        
    async def start(self, interaction : discord.Interaction):
        self.message = await interaction.edit_original_response(embed=self.embed, attachments=[self.file], view=self)
    
    async def rebind(self, interaction : discord.Interaction, *, custom_id : str, hour : Optional[str] = None):
        custom_id = re.sub(r'\D', '', custom_id)
        self.embed, file = self.try_edit_embed_message(custom_id=custom_id, hour=hour)
        
        if self.children[-1].type.name == 'select':
            self.remove_item(self.children[-1])
        select = TimeSelect(
            date=custom_id,
            times=self.search(custom_id=custom_id, get_times=True)
        )
        select.fill_options()
        if select.options and len(select.options) > 1:
            self.add_item(select)
        await interaction.response.edit_message(embed=self.embed, attachments=[file], view=self)
        
    async def on_timeout(self) -> None:
        if self.message:
            try:
                await self.message.delete()
            except:
                self.message.edit(view=None)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.ephemeral:
            return True
        
        if interaction.user != self.author:
            if interaction.locale.name == "korean":
                msg = '당신이 만든 게 아닌 것을 조작할 수 없습니다.'
            else:
                msg = "This is not yours. You don't have permission to handle it."
            await interaction.response.send_message(msg, ephemeral=True)
            return False
        return True


class TimeSelect(discord.ui.Select['WeatherPages']):
    # 셀렉트 메뉴하나는 시간 및 날씨 정보를 가지고 있어야 함
    def __init__(self, date : str = None, times : list[str] = None):
        self.times = times
        self.date = date
        super().__init__(
            placeholder='시간을 선택하세요',
            min_values=1,
            max_values=1,
            row=1,
            custom_id=f'select-{self.date}'
        )

    def fill_options(self):
        for i in self.times:
            self.add_option(
                label=f"{i[:2]}시",
                value=i,
            )
    
    async def callback(self, interaction: discord.Interaction) -> Any:
        assert self.view is not None
        value = self.values[0]     
        await self.view.rebind(interaction, custom_id=self.custom_id, hour=value)


class WeatherButton(ui.Button['WeatherPages']):
    def __init__(self, label : str = None) :
        self._label = self.label_converter(label)
        super().__init__(
            label=self._label,
            custom_id=f'button-{label}',
            style=discord.ButtonStyle.gray,
            row=0
        )
    
    def label_converter(self, label : str = None) -> str:
        transformed = "%s년 %s월 %s일" % (label[2:4], label[4:6], label[6:])
        return transformed
    
    async def callback(self, interaction: discord.Interaction) -> Any:
        # 이와 맞는 select menu를 새로이 생성하기
        assert self.view is not None
        
        for child in self.view.children:
            if child.type.name == 'button':
                child.style = discord.ButtonStyle.gray
        self.style = discord.ButtonStyle.primary
        await self.view.rebind(interaction, custom_id=self.custom_id)

