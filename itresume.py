""" Auxiliary classes for ItLib (iTunes sorting, etc.)
"""

# pylint: disable=missing-function-docstring

from tuna import itlib

class ItResume(itlib.ItLib):
    """ IT Library resumes. """
    date_format = "%Y-%m-%d"
    shown_policy = "track"	# 'track' or 'index'
    _default_last = 100
    _last_ones = "a"

    def __init__(self, xml_path="", data=None, a_filter="P", name="i"):
        super().__init__(data, a_filter, name=name)
        self._show_trackid = ItResume.shown_policy != "index"
        if xml_path:
            self.load(xml_path)
        tup = self._refreshed()
        self.alist = tup[0]

    @staticmethod
    def configure_lasts(kind:str="a", n_last:int=-1):
        a_opt, lst = kind[0], kind[1:]
        assert lst == "", f"Strange 'kind': '{kind}'"
        if a_opt == "a":
            ItResume._default_last = n_last if n_last >= 0 else 100
            ItResume._last_ones = "a"
        elif a_opt == "b":	# Show at resume, all played
            ItResume._default_last = 0
            ItResume._last_ones = "b"
        else:
            return False
        return True

    def last_n(self, num:int, order="A", pretty=True, criteria="a") -> list:
        """ Return the last 'num' entries, ordered by:
		'A': access (last played, then index n reverse order); 'a' does not reverse
		'i': by index (ascending), 'I' descending;
		--
		'a': show all; 'b' show only the ones played
	Pretty print is achieved by using pretty=True
        """
        assert len(order) <= 1, "order?"
        if not order:
            order = "I"
        if num < 0:
            return []
        assert int(num) >= 0, "simple_last_n()"
        if criteria in "a":
            lst = [
                self.resume(idx) for idx in sorted(self.get_simple("resume"))[-num:]
            ]
        elif criteria in "b":
            lst = [
                self.resume(idx) for idx in sorted(self.get_simple("resume"))[-num:]
                if self.resume(idx)[-2] > 0
            ]
        if order in "Ii":
            yet = lst if order == "i" else lst[::-1]
            if pretty:
                return [self.my_resume(item) for item in yet]
            return yet
        do_reverse = order in "AI"
        yet = sorted(
            lst,
            key=lambda x: int(x[0]) if x[-1] is None else int_timestamp(x[-1]),
            reverse=do_reverse,
        )
        if pretty:
            return [self.my_resume(item) for item in yet]
        return yet

    def my_resume(self, item:tuple):
        """ Redirecting the pretty display into the general resume_function(). """
        if self._show_trackid:
            tup = item
        else:
            # Calculate index from 'track_id'
            lst_ids = self.get_simple("track-to-index")[item[0]]
            if not lst_ids:
                return "?"
            idx = lst_ids[0]
            lst = [f"idx.{idx}"] + list(item[1:])
            tup = tuple(lst)
        astr = resume_function(tup)
        return astr

    def reload(self, xml_path=""):
        is_ok = super().reload(xml_path)
        if not is_ok:
            return False
        self.alist = self._refreshed()[0]
        return True

    def _refreshed(self) -> tuple:
        """ Returns a tuple of:
		last_n indexes
        """
        mylast = self.last_n(
            ItResume._default_last,
            criteria=ItResume._last_ones,
        )
        return (mylast,)


def int_timestamp(dttm):
    res = itlib.my_timestamp(dttm)
    return int(res)


def simple_last_n(tunes, num:int):
    """ Return the last 'num' entries at 'tunes'. """
    # tunes = itlib.ItLib(); tunes.load("itunes.xml")
    if num < 0:
        return []
    assert int(num) >= 0, "simple_last_n()"
    lst = [
        resume_function(tunes.resume(idx)) for idx in sorted(tunes.get_simple("resume"))[-num:]
    ]
    # To sort by last play, use:
    #	for item in sorted(lst, key=lambda x: int(x[0]) if x[-1] is None else itlib.my_timestamp(x[-1]), reverse=True): print(item)
    #
    # Now just return the list containing, e.g.
    #
    #	('24419', 'Filmes que me deram cabo da vida.', 'R.dio Comercial | Ricardo Ara.jo Pereira', 1, datetime.datetime(2025, 6, 28, 15, 7, 36))
    #	...
    #
    return lst


def resume_function(tup:tuple):
    """ Returns a simple readable string from the n fields at said 'resume'. """
    #print("# resume:", tup)
    s_idx, s_name, s_what, plays, dttm = tup
    s_shown = f"{s_what.replace('/', '~'):.20}"
    if len(s_shown) >= 20:
        s_shown += "[...]"
    assert plays >= 0, "Non-negative number"
    s_date = "" if dttm is None else dttm.strftime(ItResume.date_format)
    astr = f"{s_idx:>9} {s_date:>11}. {s_name} / {s_shown}"
    return astr
