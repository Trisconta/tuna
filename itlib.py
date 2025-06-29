""" Class for itunes music reader

To test:
	import importlib, itlib; importlib.reload(itlib)
	new = itlib.ItLib(); new.load("itunes.xml")
	tunes = itlib.ItLib(new, name="copy")
	# get first entry (ascii tuple)
	tup = tunes.get_simple("resume")[1]
	track_id, one = tup[0], tup[1:]

	# Following, the last 30 titles in the indexing
	for idx in sorted(tunes.get_simple("by-index"))[-30:]: print(idx, tunes.get_simple("resume")[idx])
	# Following, up to 50 titles, reverse listed, exposing the last played ones
	for cnt, idx in enumerate(sorted(tunes.get_simple("by-index"))[::-1][:50], 1):
		that = tunes.resume(idx); print(cnt, idx, "-" if that[-1] is None else that)
"""

# pylint: disable=missing-function-docstring

import datetime
import plistlib


class ItLib:
    """ IT Library class. """
    _unknown = "-"

    def __init__(self, data=None, a_filter="P", name="i"):
        self.name = name
        self._filter = a_filter
        self._x_path = ""
        self._simple = {
            "plist": {},
            "tracks": {},
            "by-index": {},		# 1..n: (track_id, track_info)
            "resume": {},
            "track-to-index": {},	# track_id: 1..n
            "outs": {},
        }
        if data is None:
            self._data = {}
        elif getattr(data, "name", None) is None:
            # This is a regulary dictionary (assuming it's ok!)
            self._data = data
        else:
            self._data = data._data
            self._x_path = data._x_path
            self._process(data._data, a_filter)

    def get_data(self):
        """ Returns own data. """
        assert self._data, "get_data()"
        assert isinstance(self._data, dict), "unexpected"
        return self._data

    def get_simple(self, key="") -> dict:
        """ Get simple dictionary. """
        if key:
            return self._simple[key]
        return self._simple

    def track(self, idx):
        """ Returns the 'track_info' (dictionary) for index='idx' """
        res = self._simple["by-index"][idx]
        return res

    def resume(self, idx):
        """ Returns the 'resume' for index='idx' """
        res = self._simple["resume"][idx]
        return res

    def set_filter(self, a_filter="P"):
        """ Sets the loading filter. Default is 'P', for 'Podcasts' only.
        """
        self._filter = a_filter

    def load(self, xml_path):
        """ Loads iTunes Music Library.xml """
        self._x_path = xml_path
        with open(xml_path, "rb") as fdin:
            idx = self._process(
                plistlib.load(fdin),
                self._filter,
            )
        is_ok = idx > 0
        return is_ok

    def reload(self, xml_path=""):
        """ Re-loads the said music library. """
        path = xml_path if xml_path else self._x_path
        if not path:
            return False
        return self.load(path)

    def _process(self, plist, a_filter):
        """ Processes 'plist' """
        dct, trk, res = {}, {}, {}
        outs = []
        tracks = plist.get('Tracks', {})
        idx = 0
        for track_id, track_info in tracks.items():
            if a_filter in ("P",):
                if track_info.get('Genre') != 'Podcast':
                    outs.append(track_id)
                    continue
            idx += 1
            name = track_info.get('Name', ItLib._unknown)
            artist = track_info.get('Artist', ItLib._unknown)
            play_count = track_info.get('Play Count', 0)
            last_played = track_info.get('Play Date UTC', None)
            dct[idx] = (track_id, track_info)
            res[idx] = (
                track_id,
                clean_name(name),
                clean_name(artist),
                play_count,
                last_played,
            )
            if track_id in trk:
                trk[track_id].append(idx)
            else:
                trk[track_id] = [idx]
        self._data = plist
        self._simple = {
            "plist": plist,
            "tracks": tracks,
            "by-index": dct,
            "track-to-index": trk,
            "resume": res,
            "outs": {
                "filtered": outs,
            },
        }
        return idx

    def check(self):
        """ Returns an empty list if all ok. """
        trk = self._simple["track-to-index"]
        lst = list(
            set([len(item) for key, item in trk.items()])
        )
        if lst != [1]:
            return ["track-to-index", lst]
        return []


def clean_name(name, alt="."):
    if isinstance(name, str):
        return ''.join(achr if ord(achr) < 127 else alt for achr in name)
    return name


def my_datetime(dttm):
    if dttm is None or stamp_is_zero(dttm):
        return datetime_zero()
    return dttm


def my_timestamp(dttm):
    return my_datetime(dttm).timestamp()


def datetime_zero():
    dttm = datetime.datetime.fromtimestamp(0)
    return dttm


def stamp_diff(t_1, t_0):
    return t_1.timestamp() - t_0.timestamp()


def stamp_is_zero(t_0):
    return stamp_diff(t_0, datetime_zero()) < 86400
