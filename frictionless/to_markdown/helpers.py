def formatMarkdownCode(s):
    return f"`{s}`"


def formatMarkdownCodeList(s):
    return [f"`{x}`" for x in s]


def formatMarkdownLinkOrText(text, options):
    href = options.hash.href
    return f"[${text}](${href})" if href else text


def formatIndent(indent):
    return "  " if indent else ""


helpers = {
    "formatMarkdownCode": formatMarkdownCode,
    "formatMarkdownCodeList": formatMarkdownCodeList,
    "formatMarkdownLinkOrText": formatMarkdownLinkOrText,
    "formatIndent": formatIndent,
    "formatMessage": lambda x: x
}
