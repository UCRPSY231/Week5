## Imports
__author__ = 'bdyetton'
import billboard
import time
import csv
import datetime
import pandas as pd
import numpy as np
import os
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint
import urllib3
urllib3.disable_warnings()

## a "pure function", a function that does not rely on anything in the download lyrics class, so written seperatly
def get_every_week_since(year, month=1, day=1):
    time_start = datetime.datetime(year=year, month=month, day=day)
    time_inc = datetime.timedelta(days=7)
    time_now = datetime.datetime.now()
    current_time = time_start
    times = []
    while current_time < time_now:
        times.append(current_time)
        current_time += time_inc
    return len(times), times

## Class def
class DownloadLyrics:
    """A quick and dirty program to download the top billboard songs from a range of genre's and then grab their lyrics from musicmix"""

    def __init__(self,charts=['hot-holiday-songs','christian-songs','country-songs','rock-songs','pop-songs','r-b-hip-hop-songs','dance-electronic-songs','latin-songs'],songs_per_week=10):
        self.charts = charts 
        swagger_client.configuration.api_key['apikey'] = os.environ['MUSICMIX_APIKEY']
        self.musicmix_lyric_instance = swagger_client.LyricsApi()
        self.musicmix_track_instance = swagger_client.TrackApi()
        self.songs_per_week = songs_per_week

    def get_all_songs_from_all_charts(self):
        """Downloads all the song indormation (w.o. lyrics) from all billboard charts."""
        chart_songs = []
        for chart in self.charts:
            chart_songs.append(self.get_all_songs_from_chart(chart,get_every_week_since(2017)))
        all_charts_df = pd.concat(chart_songs) #concatinate the list of pandas df to a single df
        all_charts_df.to_csv('BillboardLyricData.txt', sep='\t', encoding='utf-8') #write that bad boy out to file

    def get_all_songs_from_chart(self,chart_name,query_year=2017):
        
        num_weeks_to_look_back = get_every_week_since(year=query_year)
        
        #This is where we will save our downloaded data too
        songdf = pd.DataFrame(index=np.arange(0, num_weeks*self.songs_per_week), columns=('chart','title', 'artist', 'weeks', 'rank', 'query_week', 'lyrics'))
        
        #Get this weeks songs
        chart_data = billboard.ChartData(chart_name) 

        for week_idx in range(0, num_weeks):
            try:
                chart_data = billboard.ChartData(chart_name, chart_data.previousDate)
            except:
                print "Exception when getting song data for %s, %s\n" % (chart_name, chart_data.previousDate)
                continue
                
            for song_idx, song in enumerate(chart_data):
                if song_idx > self.songs_per_week:
                    break
                print('fetching data for:',song)
                try:
                    lyric_response_data = self.musicmix_lyric_instance.matcher_lyrics_get_get(q_track=song.title, q_artist=song.artist)
                    lyric_data = lyric_response_data.message.body.lyrics
                    if lyric_data is None:
                        lyrics_clean = None
                        print("Missing lyrics for %s, %s\n" % (song.title, song.artist))
                        continue
                    lyrics_clean = lyric_data.lyrics_body.replace('******* This Lyrics is NOT for Commercial use *******','')
                except ApiException as e:
                    print "Exception when getting lyrics for %s, %s: %s\n" % (e, song.title, song.artist)
                    continue
                print("Hit lyrics for %s, %s\n" % (song.title, song.artist))
                songdf.append = [chart_name,song.title, song.artist, song.weeks, song.rank, chart_data.previousDate,lyrics_clean]

        return songdf

downloader = DownloadLyrics()
downloader.get_all_songs_from_all_charts()












