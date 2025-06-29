""" Class for itunes music reader

To test:
	import itlib; import importlib; importlib.reload(itlib)
	new = itlib.ItLib(); new.load("itunes.xml")
	tunes = itlib.ItLib(new, name="copy")
	# get first entry (ascii tuple)
	tup = tunes.get_simple("resume")[1]
	track_id, one = tup[0], tup[1:]
"""

# pylint: disable=missing-function-docstring

import plistlib


class ItLib:
    """ IT Library class. """
    _unknown = "-"

    def __init__(self, data=None, a_filter="P", name="i"):
        self.name = name
        self._filter = a_filter
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

    def set_filter(self, a_filter="P"):
        """ Sets the loading filter. Default is 'P', for 'Podcasts' only.
        """
        self._filter = a_filter

    def load(self, xml_path):
        """ Loads iTunes Music Library.xml """
        with open(xml_path, "rb") as fdin:
            idx = self._process(
                plistlib.load(fdin),
                self._filter,
            )
        is_ok = idx > 0
        return is_ok

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
            last_played = track_info.get('Play Date UTC', 'Never')
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
            set([len(trk[ala]) for ala in trk])
        )
        if lst != [1]:
            return ["track-to-index", lst]
        return []


def clean_name(name, alt="."):
    if isinstance(name, str):
        return ''.join(achr if ord(achr) < 127 else alt for achr in name)
    return name
