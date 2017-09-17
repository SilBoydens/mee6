import os
import html
import aiohttp
from plugin import Plugin
from decorators import command
from xml.etree import ElementTree
from bs4 import BeautifulSoup
from collections import OrderedDict

MAL_USERNAME = os.getenv('MAL_USERNAME')
MAL_PASSWORD = os.getenv('MAL_PASSWORD')

TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')

IMGUR_ID = os.getenv('IMGUR_ID')

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

NOT_FOUND = "I didn't find anything 😢..."


class Search(Plugin):

    """
    @command(db_name='google',
             pattern='^!google (.*)',
             db_check=True,
             usage="!google search_value")
    async def google(self, message, args):
        pass
    """

    @command(db_name='youtube',
             pattern='^!youtube (.*)',
             db_check=True,
             usage="!youtube video_name")
    async def youtube(self, message, args):
        search = args[0]
        url = "https://www.googleapis.com/youtube/v3/search"
        with aiohttp.ClientSession() as session:
            async with session.get(url, params={"type": "video",
                                                "q": search,
                                                "part": "snippet",
                                                "key": GOOGLE_API_KEY}) as resp:
                data = await resp.json()
        if data["items"]:
            video = data["items"][0]
            response = "https://youtu.be/" + video["id"]["videoId"]
        else:
            response = NOT_FOUND

        await self.mee6.send_message(message.channel, response)


    @command(db_name='urban',
             pattern='!urban (.*)',
             db_check=True,
             usage="!urban dank_word")
    async def urban(self, message, args):
        search = args[0]
        url = "http://api.urbandictionary.com/v0/define"
        with aiohttp.ClientSession() as session:
            async with session.get(url, params={"term": search}) as resp:
                data = await resp.json()

        if data["list"]:
            entry = data["list"][0]
            response = "\n **{e[word]}** ```\n{e[definition]}``` \n "\
                       "**example:** {e[example]} \n"\
                       "<{e[permalink]}>".format(e=entry)
            response = response.replace('@everyone', '@ everyone').replace('@here', '@ here')
        else:
            response = NOT_FOUND
        await self.mee6.send_message(message.channel, response)

    """
    @command(db_name='gimg',
             pattern='^!gimg (.*)',
             db_check=True,
             usage="!gimg search_value")
    async def gimg(self, message, args):
        pass
    """

    @command(db_name='pokemon',
             pattern='^!pokemon (.*)',
             db_check=True,
             usage="!pokemon pokemon_name")
    async def pokemon(self, message, args):
        url = "http://veekun.com/dex/pokemon/search"
        search = args[0]
        with aiohttp.ClientSession() as session:
            async with session.get(url,
                                   params={"name": search}) as resp:
                data = await resp.text()

        if "Nothing found" in data:
            response = NOT_FOUND
        else:
            soup = BeautifulSoup(data, "html.parser")
            tds = soup.find_all("td", class_="name")[0].parent.find_all("td")

            p = OrderedDict()
            p["name"] = tds[1].text
            p["types"] = ", ".join(map(lambda img: img["title"],
                                       tds[2].find_all("img")))
            p["abilities"] = ", ".join(map(lambda a: a.text,
                                       tds[3].find_all("a")))
            p["rates"] = tds[4].find("img")["title"]
            p["egg groups"] = tds[5].text[1:-1].replace("\n", ", ")
            p["hp"] = tds[6].text
            p["atk"] = tds[7].text
            p["def"] = tds[8].text
            p["SpA"] = tds[9].text
            p["SpD"] = tds[10].text
            p["Spd"] = tds[11].text
            p["total"] = tds[12].text
            p["url"] = "http://veekun.com" + tds[1].find("a")["href"]

            with aiohttp.ClientSession() as session:
                async with session.get(p["url"]) as resp:
                    data = await resp.text()

            soup2 = BeautifulSoup(data, "html.parser")
            img = soup2.find("div",
                             id="dex-pokemon-portrait-sprite").find("img")
            p["picture"] = "http://veekun.com" + img["src"]

            response = "\n"
            for k, v in p.items():
                response += "**" + k + ":** " + v + "\n"

        await self.mee6.send_message(message.channel, response)

    @command(db_name='twitch',
             pattern='^!twitch (.*)',
             db_check=True,
             usage="!twitch streamer_name")
    async def twitch(self, message, args):
        search = args[0]
        url = "https://api.twitch.tv/kraken/search/channels"
        with aiohttp.ClientSession() as session:
            params = {
                "q": search,
                "client_id": TWITCH_CLIENT_ID,
            }
            async with session.get(url, params=params) as resp:
                data = await resp.json()

        if data["channels"]:
            channel = data["channels"][0]
            response = "\n**" + channel["display_name"] + "**: " + channel["url"]
            response += " {0[followers]} followers & {0[views]} views".format(
                channel
            )
        else:
            response = NOT_FOUND

        await self.mee6.send_message(message.channel, response)

    @command(db_name='imgur',
             pattern='^!imgur (.*)',
             db_check=True,
             usage="!imgur some_dank_search_value")
    async def imgur(self, message, args):
        search = args[0]
        url = "https://api.imgur.com/3/gallery/search/viral"
        headers = {"Authorization": "Client-ID " + IMGUR_ID}
        with aiohttp.ClientSession() as session:
            async with session.get(url,
                                   params={"q": search},
                                   headers=headers) as resp:
                data = await resp.json()

        if data["data"]:
            result = data["data"][0]
            response = result["link"]
        else:
            response = NOT_FOUND

        await self.mee6.send_message(message.channel, response)

    """
    @command(db_name='wiki',
             pattern='^!wiki (.*)',
             db_check=True,
             usage="!wiki search_value")
    async def wiki(self, message, args):
        pass
    """

    @command(db_name='manga',
             pattern='!manga (.*)',
             db_check=True,
             usage="!manga manga_name")
    async def manga(self, message, args):
        search = args[0]
        auth = aiohttp.BasicAuth(login=MAL_USERNAME, password=MAL_PASSWORD)
        url = 'https://myanimelist.net/api/manga/search.xml'
        params = {'q': search}
        with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(url, params=params) as response:
                data = await response.text()

        if data == "":
            await self.mee6.send_message(message.channel,
                                         "I didn't find anything :cry:...")
            return

        root = ElementTree.fromstring(data)
        if len(root) == 0:
            await self.mee6.send_message(message.channel,
                                         "Sorry, I didn't find anything :cry:"
                                         "...")
        elif len(root) == 1:
            entry = root[0]
        else:
            msg = "**Please choose one by giving its number**\n"
            msg += "\n".join(['{} - {}'.format(n+1, entry[1].text)
                              for n, entry in enumerate(root) if n < 10])

            await self.mee6.send_message(message.channel, msg)

            def check(m): return m.content in map(str, range(1, len(root)+1))
            resp = await self.mee6.wait_for_message(author=message.author,
                                                    check=check,
                                                    timeout=20)
            if resp is None:
                return

            entry = root[int(resp.content)-1]

        switcher = [
            'english',
            'score',
            'type',
            'episodes',
            'volumes',
            'chapters',
            'status',
            'start_date',
            'end_date',
            'synopsis'
            ]

        msg = '\n**{}**\n\n'.format(entry.find('title').text)
        for k in switcher:
            spec = entry.find(k)
            if spec is not None and spec.text is not None:
                msg += '**{}** {}\n'.format(k.capitalize()+':',
                                            html.unescape(spec.text.replace(
                                                '<br />',
                                                ''
                                            )))
        msg += 'https://myanimelist.net/manga/{}'.format(entry.find('id').text)

        await self.mee6.send_message(message.channel,
                                     msg)

    @command(db_name='anime',
             pattern='!anime (.*)',
             db_check=True,
             usage="!anime anime_name")
    async def anime(self, message, args):
        search = args[0]
        auth = aiohttp.BasicAuth(MAL_USERNAME, password=MAL_PASSWORD)
        url = 'https://myanimelist.net/api/anime/search.xml'
        params = {'q': search}
        with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(url, params=params) as response:
                data = await response.text()

        if data == "":
            await self.mee6.send_message(message.channel,
                                         "I didn't find anything :cry:...")
            return

        root = ElementTree.fromstring(data)
        if len(root) == 0:
            await self.mee6.send_message(message.channel,
                                         "Sorry, I didn't find anything :cry:"
                                         "...")
        elif len(root) == 1:
            entry = root[0]
        else:
            msg = "**Please choose one by giving its number**\n"
            msg += "\n".join(['{} - {}'.format(n+1, entry[1].text)
                              for n, entry in enumerate(root) if n < 10])

            await self.mee6.send_message(message.channel, msg)

            def check(m): return m.content in map(str, range(1, len(root)+1))
            resp = await self.mee6.wait_for_message(author=message.author,
                                                    check=check,
                                                    timeout=20)
            if resp is None:
                return

            entry = root[int(resp.content)-1]

        switcher = [
            'english',
            'score',
            'type',
            'episodes',
            'volumes',
            'chapters',
            'status',
            'start_date',
            'end_date',
            'synopsis'
            ]

        msg = '\n**{}**\n\n'.format(entry.find('title').text)
        for k in switcher:
            spec = entry.find(k)
            if spec is not None and spec.text is not None:
                msg += '**{}** {}\n'.format(k.capitalize()+':',
                                            html.unescape(spec.text.replace(
                                                '<br />',
                                                ''
                                            )))
        msg += 'https://myanimelist.net/anime/{}'.format(entry.find('id').text)

        await self.mee6.send_message(message.channel,
                                     msg)
