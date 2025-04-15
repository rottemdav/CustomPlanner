from types import MappingProxyType

COURSE_NUMS = MappingProxyType({
    "אותות אקראיים": "00440202",
    "מערכות לומדות": "00460195",
    "ענ\"ת": "00460200",
    "מעגלים אלקטרוניים": "00440137",
    "מל\"מ": "00440127"
})

COLORS_PALETTE = MappingProxyType(
    {
        "light-orange": "#FFDCCC",
        "light-purple": "#B7B1F2",
        "light-pink": "#FDB7EA",
        "light-yellow": "#FBF3B9",
        "grey": "E0E0E0"
    }
)

LAYERS_COLORS = MappingProxyType(
    {
        "אישי": "light-pink",
        "לימודים": "light-yellow",
        "כללי": "grey"
    }
)