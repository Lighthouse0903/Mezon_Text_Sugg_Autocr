import re

TONE_CHARS = "sfrxj"
FAMILY_RULES = {
    "me": "mẹ",
    "mme": "mẹ",
    "mje": "mẹ",
    "mej": "mẹ",
    "mef": "mẹ",
    "bo": "bố",
    "boj": "bố",
    "bof": "bố",
    "bô": "bố",
    "cha": "cha",
    "chaof": "chào",
    "ong": "ông",
    "ongf": "ông",
    "onng": "ông",
    "ba": "bà",
    "baj": "bà",
    "baf": "bà",
    "anh": "anh",
    "chi": "chị",
    "chij": "chị",
    "em": "em",
    "con": "con",
    "chau": "cháu",
    "chauf": "cháu",
}

OBJECT_RULES = {
    "ban": "bàn",
    "banf": "bàn",
    "bajn": "bàn",
    "ghe": "ghế",
    "ghef": "ghế",
    "ghes": "ghế",
    "ghej": "ghế",
    "giuong": "giường",
    "giuon": "giường",
    "giuongf": "giường",
    "den": "đèn",
    "denf": "đèn",
    "denj": "đèn",
    "tu": "tủ",
    "tuf": "tủ",
    "tuj": "tủ",
    "nha": "nhà",
    "nhaf": "nhà",
    "nhaj": "nhà",
    "bep": "bếp",
    "bepj": "bếp",
    "bepf": "bếp",
    "banh": "bánh",
    "banhf": "bánh",
    "banhj": "bánh",
    "giuongf": "giường",
    "banan": "bàn ăn",
    "sofa": "sofa",
}

NATURE_RULES = {
    "troi": "trời",
    "trowi": "trời",
    "trowif": "trời",
    "trowiff": "trời",
    "troiwf": "trời",
    "troiwff": "trời",
    "troiw": "trời",
    "trowiif": "trời",
    "troj": "trời",
    "troif": "trời",
    "trwi": "trời",
    "dep": "đẹp",
    "depj": "đẹp",
    "depf": "đẹp",
    "ddep": "đẹp",
    "đep": "đẹp",
    "mua": "mưa",
    "muaf": "mưa",
    "muwaf": "mưa",
    "muwas": "mưa",
    "nang": "nắng",
    "naws": "nắng",
    "nangf": "nắng",
    "lanh": "lạnh",
    "lanhf": "lạnh",
    "lajnh": "lạnh",
    "gio": "gió",
    "giof": "gió",
    "gioj": "gió",
    "bien": "biển",
    "bienj": "biển",
    "bienf": "biển",
    "nui": "núi",
    "nuif": "núi",
    "nuij": "núi",
    "dat": "đất",
    "datj": "đất",
    "datf": "đất",
    "tro": "tro",
    "may": "mây",
    "mayf": "mây",
    "mayj": "mây",
}

SKY_RULES = {
    "troi": "trời",
    "trowi": "trời",
    "trowif": "trời",
    "trowiff": "trời",
    "troiwf": "trời",
    "troiwff": "trời",
    "troiw": "trời",
    "truoi": "trời",
    "troiif": "trời",
}

ACTION_RULES = {
    "lam": "làm",
    "lamf": "làm",
    "lamj": "làm",
    "yeu": "yêu",
    "yeuf": "yêu",
    "yeuj": "yêu",
    "yeue": "yêu",
    "hoc": "học",
    "hocj": "học",
    "hocf": "học",
    "chao": "chào",
    "chaof": "chào",
    "chaoj": "chào",
    "chaofof": "chào",
    "an": "ăn",
    "anf": "ăn",
    "anj": "ăn",
    "ngu": "ngủ",
    "nguf": "ngủ",
    "nguj": "ngủ",
    "nguw": "ngủ",
    "choi": "chơi",
    "choif": "chơi",
    "choij": "chơi",
    "doc": "đọc",
    "docf": "đọc",
    "dojf": "đọc",
    "noi": "nói",
    "noif": "nói",
    "noij": "nói",
    "di": "đi",
    "dif": "đi",
    "dij": "đi",
    "viet": "viết",
    "vietj": "viết",
    "vietf": "viết",
    "nghe": "nghe",
    "nghef": "nghe",
    "uom": "ươm",
    "xem": "xem",
}

PLACE_RULES = {
    "truong": "trường",
    "truongf": "trường",
    "lop": "lớp",
    "lopj": "lớp",
    "lopf": "lớp",
    "cho": "chợ",
    "chof": "chợ",
    "choj": "chợ",
    "nha": "nhà",
    "nhaf": "nhà",
    "truonghoc": "trường học",
    "congvien": "công viên",
    "congvienf": "công viên",
    "bien": "biển",
    "bienj": "biển",
    "bienf": "biển",
    "nui": "núi",
    "nuif": "núi",
    "rung": "rừng",
    "rungf": "rừng",
    "pho": "phố",
    "phof": "phố",
    "duong": "đường",
    "duongf": "đường",
    "nhaang": "nhà hàng",
    "quancafe": "quán cafe",
}

EMOTION_RULES = {
    "vui": "vui",
    "buon": "buồn",
    "buonj": "buồn",
    "buonf": "buồn",
    "gian": "giận",
    "gianf": "giận",
    "met": "mệt",
    "metf": "mệt",
    "metj": "mệt",
    "doj": "đói",
    "doi": "đói",
    "doif": "đói",
    "khat": "khát",
    "khatj": "khát",
    "khatf": "khát",
    "to": "tốt",
    "toj": "tốt",
    "tof": "tốt",
    "xau": "xấu",
    "xauf": "xấu",
    "xauj": "xấu",
    "dep": "đẹp",
    "depj": "đẹp",
    "depf": "đẹp",
    "hon": "hơn",
    "tot": "tốt",
    "totf": "tốt",
    "totj": "tốt",
    "kem": "kém",
    "kemf": "kém",
    "kemj": "kém",
}
EXTRA_RULES = {
    "com": "cơm",
    "ngoifa": "ngoài",
    "ngoif": "ngoài",
    "ngoiaf": "ngoài",
    "ngoifaf": "ngoài",
    "phsoo": "phố",
    "phsoo": "phố",
    "phos": "phố",
    "soong": "sông",
    "soojng": "sông",
    "lutj": "lụt",
    "luf": "lụt",
    "xayry": "xảy",
    "xayr": "xảy",
    "xary": "xảy",
    "mawcsc": "mắc cạn",
    "macsc": "mắc cạn",
    "cas": "cá",
    "hể": "có thể",
    "he": "hể",
}

ALL_RULES = {}
for group in (
    FAMILY_RULES,
    OBJECT_RULES,
    NATURE_RULES,
    ACTION_RULES,
    PLACE_RULES,
    EMOTION_RULES,
    EXTRA_RULES,
    SKY_RULES,
):
    ALL_RULES.update(group)


def apply_hard_rules(word: str) -> str:
    w = word.lower().strip()
    if w in ALL_RULES:
        return ALL_RULES[w]

    if re.match(r"^tro[w]*[a-z]*[sfrxj]*$", w):
        return "trời"
    if re.match(r"^chao[a-z]*[sfrxj]*$", w):
        return "chào"
    if re.match(r"^[dđ]ep[a-z]*[sfrxj]*$", w):
        return "đẹp"
    if re.match(r"^mu[aă][a-z]*[sfrxj]*$", w):
        return "mưa"
    if re.match(r"^yeu[a-z]*[sfrxj]*$", w):
        return "yêu"
    if re.match(r"^nh[aă][a-z]*[sfrxj]*$", w):
        return "nhà"
    if re.match(r"^truong[a-z]*[sfrxj]*$", w):
        return "trường"
    if re.match(r"^ban[a-z]*[sfrxj]*$", w):
        return "bàn"
    if re.match(r"^ghe[a-z]*[sfrxj]*$", w):
        return "ghế"
    if re.match(r"^bo[a-z]*[sfrxj]*$", w):
        return "bố"
    if re.match(r"^me[a-z]*[sfrxj]*$", w):
        return "mẹ"
    if re.match(r"^ba[a-z]*[sfrxj]*$", w):
        return "bà"
    if re.match(r"^an[a-z]*[sfrxj]*$", w):
        return "ăn"
    if re.match(r"^ngu[a-z]*[sfrxj]*$", w):
        return "ngủ"
    if re.match(r"^vui[a-z]*[sfrxj]*$", w):
        return "vui"
    if re.match(r"^buon[a-z]*[sfrxj]*$", w):
        return "buồn"
    if re.match(r"^met[a-z]*[sfrxj]*$", w):
        return "mệt"
    if re.match(r"^doi[a-z]*[sfrxj]*$", w):
        return "đói"
    if re.match(r"^khat[a-z]*[sfrxj]*$", w):
        return "khát"
    if re.match(r"^tot[a-z]*[sfrxj]*$", w):
        return "tốt"
    if re.match(r"^xau[a-z]*[sfrxj]*$", w):
        return "xấu"
    if re.match(r"^lanh[a-z]*[sfrxj]*$", w):
        return "lạnh"

    return word
