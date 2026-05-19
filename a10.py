import re, string, calendar, requests, time
from wikipedia import WikipediaPage
import wikipedia
from bs4 import BeautifulSoup
from match import match
from typing import List, Callable, Tuple, Any, Match


def get_page_html(title: str) -> str:
    for attempt in range(5):
        try:
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "parse",
                    "page": title,
                    "prop": "text",
                    "format": "json",
                    "redirects": True,
                },
                headers={"User-Agent": "intro-ai-class/1.0"},
                timeout=10
            )
        except requests.exceptions.ConnectTimeout:
            print(f"Connection timed out, retrying '{title}'... (attempt {attempt+1}/5)")
            time.sleep(5)
            continue

        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", 5))
            print(f"Rate limited — waiting {wait}s before retrying '{title}'...")
            time.sleep(wait)
            continue
        if response.status_code == 200 and response.text.strip():
            data = response.json()
            if "error" not in data:
                time.sleep(3)
                return data["parse"]["text"]["*"]

    raise ConnectionError(f"Could not retrieve Wikipedia page for '{title}' after 5 attempts")


def get_first_infobox_text(html: str) -> str:
    """Gets first infobox html from a Wikipedia page (summary box)

    Args:
        html - the full html of the page

    Returns:
        html of just the first infobox
    """
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(class_="infobox")

    if not results:
        raise LookupError("Page has no infobox")
    return results[0].text


def clean_text(text: str) -> str:
    """Cleans given text removing non-ASCII characters and duplicate spaces & newlines

    Args:
        text - text to clean

    Returns:
        cleaned text
    """
    only_ascii = "".join([char if char in string.printable else " " for char in text])
    no_dup_spaces = re.sub(" +", " ", only_ascii)
    no_dup_newlines = re.sub("\n+", "\n", no_dup_spaces)
    return no_dup_newlines


def get_match(
    text: str,
    pattern: str,
    error_text: str = "Page doesn't appear to have the property you're expecting",
) -> Match:
    """Finds regex matches for a pattern

    Args:
        text - text to search within
        pattern - pattern to attempt to find within text
        error_text - text to display if pattern fails to match

    Returns:
        text that matches
    """
    p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    match = p.search(text)

    if not match:
        raise AttributeError(error_text)
    return match



def get_polar_radius(planet_name: str) -> str:
    """Gets the radius of the given planet

    Args:
        planet_name - name of the planet to get radius of

    Returns:
        radius of the given planet
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(planet_name)))
    pattern = r"(?:Polar radius|Mean radius)(?:[^\d]*)(?P<radius>[\d,.]+)(?:.*?)km"
    error_text = "Page infobox has no polar radius information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group("radius")


def get_birth_date(name: str) -> str:
    """Gets birth date of the given person

    Args:
        name - name of the person

    Returns:
        birth date of the given person
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(name)))
    pattern = r"(?:Born\D*)(?P<birth>\d{4}-\d{2}-\d{2})"
    error_text = (
        "Page infobox has no birth information (at least none in xxxx-xx-xx format)"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("birth")



def get_birth_year(name: str) -> str:
    """Gets birth date of the given person

    Args:
        name - name of the person

    Returns:
        birth date of the given person
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(name)))
    pattern = r"(?:Born\D*)(?P<year>\d{4})"
    error_text = (
        "Page infobox has no birth information (at least none in xxxx-xx-xx format)"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("year")



def get_release_date(title: str) -> str:
    """Gets release date of the given game

    Args:
        title - title of the game

    Returns:
        release date of the given game
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(title)))
    print(infobox_text)
    pattern = r"(?:Release\D*\n*)(?P<release>[\w, ]+)"
    error_text = (
        "Page infobox has no release information (at least none in xxxx format)"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("release")


def get_developer(title: str) -> str:
    """Gets the developers of the given game

    Args:
        title - title of the game

    Returns:
        publisher of the given game
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(title)))
    print(infobox_text)
    pattern = r"(?:Developer)(?P<developer>.*?)(?:Publisher)"
    error_text = (
        "Page infobox has no developer information (at least none in xxxx format)"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("developer")


def get_designer(title: str) -> str:
    """Gets the developers of the given game

    Args:
        title - title of the game

    Returns:
        publisher of the given game
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(title)))
    print(infobox_text)
    pattern = r"(?:Designers|Designer)(?P<designer>.*?)(?:Artist|Programmers)"
    error_text = (
        "Page infobox has no developer information (at least none in xxxx format)"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("designer")


def get_artist(title: str) -> str:
    """Gets the artists of the given game

    Args:
        title - title of the game

    Returns:
        artists of the given game
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(title)))
    print(infobox_text)
    pattern = r"(?:Artists|Artist)(?P<artist>.*?)(?:Composer|Writer)"
    error_text = (
        "Page infobox has no developer information (at least none in xxxx format)"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("artist")


# below are a set of actions. Each takes a list argument and returns a list of answers
# according to the action and the argument. It is important that each function returns a
# list of the answer(s) and not just the answer itself.


def birth_date(matches: List[str]) -> List[str]:
    """Returns birth date of named person in matches

    Args:
        matches - match from pattern of person's name to find birth date of

    Returns:
        birth date of named person
    """
    return [get_birth_date(" ".join(matches))]


def release_date(matches: List[str]) -> List[str]:
    """Returns release date of game in matches

    Args:
        matches - match from pattern of Game's name to find release date of

    Returns:
        release date of game
    """
    return [get_release_date(" ".join(matches))]


def developer(matches: List[str]) -> List[str]:
    """Returns release date of game in matches

    Args:
        matches - match from pattern of Game's name to find release date of

    Returns:
        release date of game
    """
    return [get_developer(" ".join(matches))]


def birth_year(matches: List[str]) -> List[str]:
    """Returns birth year of named person in matches

    Args:
        matches - match from pattern of person's name to find birth year of

    Returns:
        birth year of named person
    """
    return [get_birth_year(" ".join(matches))]


def polar_radius(matches: List[str]) -> List[str]:
    """Returns polar radius of planet in matches

    Args:
        matches - match from pattern of planet to find polar radius of

    Returns:
        polar radius of planet
    """
    return [get_polar_radius(matches[0])]


def designer(matches: List[str]) -> List[str]:
    """Returns designer of game in matches

    Args:
        matches - match from pattern of Game's name to find designer of

    Returns:
        designer of game
    """
    return [get_designer(" ".join(matches))]


def artist(matches: List[str]) -> List[str]:
    """Returns artist of game in matches

    Args:
        matches - match from pattern of Game's name to find artist of

    Returns:
        artist of game
    """
    return [get_artist(" ".join(matches))]


# dummy argument is ignored and doesn't matter
def bye_action(dummy: List[str]) -> None:
    raise KeyboardInterrupt


# type aliases to make pa_list type more readable, could also have written:
# pa_list: List[Tuple[List[str], Callable[[List[str]], List[Any]]]] = [...]
Pattern = List[str]
Action = Callable[[List[str]], List[Any]]

# The pattern-action list for the natural language query system. It must be declared
# here, after all of the function definitions
pa_list: List[Tuple[Pattern, Action]] = [
    ("when was % born".split(), birth_date),
    ("what year was % born".split(), birth_year),
    ("when was % released".split(), release_date),
    ("who was % developed by".split(), developer),
    ("what is the polar radius of %".split(), polar_radius),
    ("who was % designed by".split(), designer),
    ("who was % artists".split(), artist),
    (["bye"], bye_action),
]


def search_pa_list(src: List[str]) -> List[str]:
    """Takes source, finds matching pattern and calls corresponding action. If it finds
    a match but has no answers it returns ["No answers"]. If it finds no match it
    returns ["I don't understand"].

    Args:
        source - a phrase represented as a list of words (strings)

    Returns:
        a list of answers. Will be ["I don't understand"] if it finds no matches and
        ["No answers"] if it finds a match but no answers
    """
    for pat, act in pa_list:
        mat = match(pat, src)
        if mat is not None:
            answer = act(mat)
            return answer if answer else ["No answers"]

    return ["I don't understand"]


def query_loop() -> None:
    """The simple query loop. The try/except structure is to catch Ctrl-C or Ctrl-D
    characters and exit gracefully"""
    print("Welcome to the wikipedia chatbot!\n")
    while True:
        try:
            print()
            query = input("Your query? ").replace("?", "").lower().split()
            answers = search_pa_list(query)
            for ans in answers:
                print(ans)

        except (KeyboardInterrupt, EOFError):
            break

    print("\nSo long!\n")


# uncomment the next line once you've implemented everything are ready to try it out
query_loop()
