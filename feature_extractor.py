import re
import urllib.parse
import ipaddress

import pandas as pd
import requests
import tldextract
from bs4 import BeautifulSoup


# ============================================================
# EXACT 41 FEATURES
# ============================================================

FEATURE_NAMES = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
    "LineOfCode",
    "LargestLineLength",
    "HasTitle",
    "HasFavicon",
    "Robots",
    "IsResponsive",
    "NoOfURLRedirect",
    "NoOfSelfRedirect",
    "HasDescription",
    "NoOfPopup",
    "NoOfiFrame",
    "HasExternalFormSubmit",
    "HasSocialNet",
    "HasSubmitButton",
    "HasHiddenFields",
    "HasPasswordField",
    "HasCopyrightInfo",
    "NoOfImage",
    "NoOfCSS",
    "NoOfJS",
    "NoOfSelfRef",
    "NoOfEmptyRef",
    "NoOfExternalRef"
]


HTML_FEATURE_NAMES = [
    "LineOfCode",
    "LargestLineLength",
    "HasTitle",
    "HasFavicon",
    "Robots",
    "IsResponsive",
    "NoOfURLRedirect",
    "NoOfSelfRedirect",
    "HasDescription",
    "NoOfPopup",
    "NoOfiFrame",
    "HasExternalFormSubmit",
    "HasSocialNet",
    "HasSubmitButton",
    "HasHiddenFields",
    "HasPasswordField",
    "HasCopyrightInfo",
    "NoOfImage",
    "NoOfCSS",
    "NoOfJS",
    "NoOfSelfRef",
    "NoOfEmptyRef",
    "NoOfExternalRef"
]


# ============================================================
# USER AGENT
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    )
}


# ============================================================
# CLEAN URL
# ============================================================

def clean_url(url):

    url = str(url).strip()

    if not url:
        raise ValueError("URL cannot be empty.")

    # Handle markdown URL:
    # [https://google.com](https://google.com)
    match = re.search(
        r'\[([^\]]+)\]\((https?://[^)]+)\)',
        url
    )

    if match:
        url = match.group(2)

    # Remove quotes
    url = url.strip('"')
    url = url.strip("'")

    # Remove spaces
    url = url.strip()

    # Add protocol
    if not re.match(
        r"^[a-zA-Z][a-zA-Z0-9+.-]*://",
        url
    ):
        url = "https://" + url

    return url


# ============================================================
# URL FEATURES
# ============================================================

def extract_url_features(url):

    features = {}

    parsed = urllib.parse.urlparse(url)

    domain = parsed.hostname or ""

    # --------------------------------------------------------
    # URL LENGTH
    #
    # Do not include a trailing slash added by redirect.
    # --------------------------------------------------------

    url_for_features = url.rstrip("/")

    features["URLLength"] = float(len(url_for_features))

    # --------------------------------------------------------
    # DOMAIN LENGTH
    # --------------------------------------------------------

    features["DomainLength"] = float(len(domain))

    # --------------------------------------------------------
    # DOMAIN IS IP
    # --------------------------------------------------------

    try:

        ipaddress.ip_address(domain)

        features["IsDomainIP"] = 1.0

    except ValueError:

        features["IsDomainIP"] = 0.0

    # --------------------------------------------------------
    # TLD
    # --------------------------------------------------------

    extracted = tldextract.extract(url)

    features["TLDLength"] = float(
        len(extracted.suffix)
    )

    # --------------------------------------------------------
    # SUBDOMAIN
    # --------------------------------------------------------

    if extracted.subdomain:

        features["NoOfSubDomain"] = float(
            len(extracted.subdomain.split("."))
        )

    else:

        features["NoOfSubDomain"] = 0.0

    # --------------------------------------------------------
    # OBFUSCATION
    # --------------------------------------------------------

    obfuscated_matches = re.findall(
        r"%[0-9A-Fa-f]{2}",
        url
    )

    obfuscated = len(obfuscated_matches)

    features["HasObfuscation"] = float(
        1 if obfuscated > 0 else 0
    )

    features["NoOfObfuscatedChar"] = float(
        obfuscated
    )

    features["ObfuscationRatio"] = float(
        obfuscated / len(url_for_features)
        if len(url_for_features) > 0
        else 0
    )

    # --------------------------------------------------------
    # LETTERS
    # --------------------------------------------------------

    letters = len(
        re.findall(
            r"[A-Za-z]",
            url_for_features
        )
    )

    features["NoOfLettersInURL"] = float(
        letters
    )

    features["LetterRatioInURL"] = float(
        letters / len(url_for_features)
        if len(url_for_features) > 0
        else 0
    )

    # --------------------------------------------------------
    # DIGITS
    # --------------------------------------------------------

    digits = len(
        re.findall(
            r"[0-9]",
            url_for_features
        )
    )

    features["NoOfDegitsInURL"] = float(
        digits
    )

    features["DegitRatioInURL"] = float(
        digits / len(url_for_features)
        if len(url_for_features) > 0
        else 0
    )

    # --------------------------------------------------------
    # EQUALS
    # --------------------------------------------------------

    features["NoOfEqualsInURL"] = float(
        url.count("=")
    )

    # --------------------------------------------------------
    # QUESTION MARK
    # --------------------------------------------------------

    features["NoOfQMarkInURL"] = float(
        url.count("?")
    )

    # --------------------------------------------------------
    # AMPERSAND
    # --------------------------------------------------------

    features["NoOfAmpersandInURL"] = float(
        url.count("&")
    )

    # --------------------------------------------------------
    # SPECIAL CHARACTERS
    # --------------------------------------------------------

    special = len(
        re.findall(
            r"[^A-Za-z0-9]",
            url_for_features
        )
    )

    features["NoOfOtherSpecialCharsInURL"] = float(
        special
    )

    features["SpacialCharRatioInURL"] = float(
        special / len(url_for_features)
        if len(url_for_features) > 0
        else 0
    )

    # --------------------------------------------------------
    # HTTPS
    # --------------------------------------------------------

    features["IsHTTPS"] = float(
        1 if parsed.scheme.lower() == "https" else 0
    )

    return features


# ============================================================
# HTML FEATURES
# ============================================================

def get_html_features(url):

    features = {
        name: 0.0
        for name in HTML_FEATURE_NAMES
    }

    diagnostics = {
        "html_fetch_ok": False,
        "html_status": None,
        "final_url": url,
        "error": ""
    }

    try:

        # ----------------------------------------------------
        # DOWNLOAD PAGE
        # ----------------------------------------------------

        response = requests.get(
            url,
            timeout=10,
            headers=HEADERS,
            allow_redirects=True
        )

        diagnostics["html_status"] = response.status_code
        diagnostics["final_url"] = response.url

        print(
            "HTML STATUS:",
            response.status_code
        )

        print(
            "FINAL URL:",
            response.url
        )

        if response.status_code != 200:

            diagnostics["error"] = (
                f"HTTP {response.status_code}"
            )

            return features, diagnostics

        html = response.text

        if not html.strip():

            diagnostics["error"] = "Empty HTML"

            return features, diagnostics

        # ----------------------------------------------------
        # BEAUTIFULSOUP
        # ----------------------------------------------------

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # ----------------------------------------------------
        # LINE OF CODE
        # ----------------------------------------------------

        lines = html.splitlines()

        features["LineOfCode"] = float(
            len(lines)
        )

        # ----------------------------------------------------
        # LARGEST LINE
        # ----------------------------------------------------

        features["LargestLineLength"] = float(
            max(
                (len(line) for line in lines),
                default=0
            )
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        features["HasTitle"] = float(
            1 if soup.find("title") else 0
        )

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        description = soup.find(
            "meta",
            attrs={
                "name": re.compile(
                    r"^description$",
                    re.I
                )
            }
        )

        features["HasDescription"] = float(
            1 if description else 0
        )

        # ----------------------------------------------------
        # FAVICON
        # ----------------------------------------------------

        favicon = False

        for link in soup.find_all("link"):

            rel = link.get("rel", [])

            if isinstance(rel, str):
                rel = [rel]

            rel = [
                str(x).lower()
                for x in rel
            ]

            if any(
                "icon" in x
                for x in rel
            ):
                favicon = True
                break

        features["HasFavicon"] = float(
            1 if favicon else 0
        )

        # ----------------------------------------------------
        # ROBOTS
        # ----------------------------------------------------

        robots_url = urllib.parse.urljoin(
            response.url,
            "/robots.txt"
        )

        try:

            robots_response = requests.get(
                robots_url,
                timeout=3,
                headers=HEADERS
            )

            features["Robots"] = float(
                1
                if robots_response.status_code == 200
                else 0
            )

        except Exception:

            features["Robots"] = 0.0

        # ----------------------------------------------------
        # RESPONSIVE
        # ----------------------------------------------------

        viewport = soup.find(
            "meta",
            attrs={
                "name": re.compile(
                    r"^viewport$",
                    re.I
                )
            }
        )

        features["IsResponsive"] = float(
            1 if viewport else 0
        )

        # ----------------------------------------------------
        # IMAGES
        # ----------------------------------------------------

        features["NoOfImage"] = float(
            len(
                soup.find_all("img")
            )
        )

        # ----------------------------------------------------
        # CSS
        # ----------------------------------------------------

        css_count = 0

        for link in soup.find_all("link"):

            rel = link.get("rel", [])

            if isinstance(rel, str):
                rel = [rel]

            rel = [
                str(x).lower()
                for x in rel
            ]

            if "stylesheet" in rel:

                css_count += 1

        features["NoOfCSS"] = float(
            css_count
        )

        # ----------------------------------------------------
        # JAVASCRIPT
        # ----------------------------------------------------

        features["NoOfJS"] = float(
            len(
                soup.find_all("script")
            )
        )

        # ----------------------------------------------------
        # IFRAME
        # ----------------------------------------------------

        features["NoOfiFrame"] = float(
            len(
                soup.find_all("iframe")
            )
        )

        # ----------------------------------------------------
        # PASSWORD
        # ----------------------------------------------------

        password = soup.find(
            "input",
            attrs={
                "type": re.compile(
                    r"^password$",
                    re.I
                )
            }
        )

        features["HasPasswordField"] = float(
            1 if password else 0
        )

        # ----------------------------------------------------
        # SUBMIT
        # ----------------------------------------------------

        submit = soup.find(
            ["button", "input"],
            attrs={
                "type": re.compile(
                    r"^(submit|button)$",
                    re.I
                )
            }
        )

        features["HasSubmitButton"] = float(
            1 if submit else 0
        )

        # ----------------------------------------------------
        # HIDDEN
        # ----------------------------------------------------

        hidden = soup.find(
            "input",
            attrs={
                "type": re.compile(
                    r"^hidden$",
                    re.I
                )
            }
        )

        features["HasHiddenFields"] = float(
            1 if hidden else 0
        )

        # ----------------------------------------------------
        # POPUPS
        # ----------------------------------------------------

        html_lower = html.lower()

        popup_patterns = [
            "window.open",
            "alert(",
            "prompt(",
            "confirm("
        ]

        features["NoOfPopup"] = float(
            sum(
                html_lower.count(pattern)
                for pattern in popup_patterns
            )
        )

        # ----------------------------------------------------
        # SOCIAL NETWORK
        # ----------------------------------------------------

        social_domains = [
            "facebook.com",
            "twitter.com",
            "x.com",
            "instagram.com",
            "linkedin.com",
            "youtube.com",
            "tiktok.com",
            "pinterest.com"
        ]

        features["HasSocialNet"] = float(
            1
            if any(
                domain in html_lower
                for domain in social_domains
            )
            else 0
        )

        # ----------------------------------------------------
        # COPYRIGHT
        # ----------------------------------------------------

        features["HasCopyrightInfo"] = float(
            1
            if (
                "copyright" in html_lower
                or "©" in html
            )
            else 0
        )

        # ----------------------------------------------------
        # CURRENT DOMAIN
        # ----------------------------------------------------

        current_domain = (
            urllib.parse.urlparse(
                response.url
            ).hostname
        )

        current_domain = (
            current_domain.lower()
            if current_domain
            else ""
        )

        # ----------------------------------------------------
        # EXTERNAL FORM
        # ----------------------------------------------------

        external_form = 0

        for form in soup.find_all("form"):

            action = form.get(
                "action",
                ""
            ).strip()

            if not action:
                continue

            absolute_action = (
                urllib.parse.urljoin(
                    response.url,
                    action
                )
            )

            action_domain = (
                urllib.parse.urlparse(
                    absolute_action
                ).hostname
            )

            if action_domain:

                action_domain = (
                    action_domain.lower()
                )

                if (
                    current_domain
                    and action_domain != current_domain
                ):

                    external_form = 1
                    break

        features[
            "HasExternalFormSubmit"
        ] = float(external_form)

        # ----------------------------------------------------
        # LINKS
        # ----------------------------------------------------

        external = 0
        self_ref = 0
        empty = 0

        links = soup.find_all(
            "a",
            href=True
        )

        for link in links:

            href = link.get(
                "href",
                ""
            ).strip()

            if href in (
                "",
                "#",
                "javascript:void(0)",
                "javascript:void(0);"
            ):

                empty += 1
                continue

            absolute_url = (
                urllib.parse.urljoin(
                    response.url,
                    href
                )
            )

            link_domain = (
                urllib.parse.urlparse(
                    absolute_url
                ).hostname
            )

            if not link_domain:

                self_ref += 1

            elif (
                current_domain
                and link_domain.lower()
                == current_domain
            ):

                self_ref += 1

            else:

                external += 1

        features["NoOfExternalRef"] = float(
            external
        )

        features["NoOfSelfRef"] = float(
            self_ref
        )

        features["NoOfEmptyRef"] = float(
            empty
        )

        # ----------------------------------------------------
        # REDIRECTS
        # ----------------------------------------------------

        features["NoOfURLRedirect"] = float(
            len(response.history)
        )

        # ----------------------------------------------------
        # SELF REDIRECTS
        # ----------------------------------------------------

        self_redirects = 0

        for redirect in response.history:

            old_domain = (
                urllib.parse.urlparse(
                    redirect.url
                ).hostname
            )

            location = redirect.headers.get(
                "Location",
                ""
            )

            if old_domain and location:

                new_url = urllib.parse.urljoin(
                    redirect.url,
                    location
                )

                new_domain = (
                    urllib.parse.urlparse(
                        new_url
                    ).hostname
                )

                if (
                    new_domain
                    and old_domain.lower()
                    == new_domain.lower()
                ):

                    self_redirects += 1

        features["NoOfSelfRedirect"] = float(
            self_redirects
        )

        diagnostics["html_fetch_ok"] = True

    except Exception as e:

        diagnostics["error"] = str(e)

        print(
            "HTML extraction warning:",
            str(e)
        )

    return features, diagnostics


# ============================================================
# MAIN FEATURE EXTRACTION
# ============================================================

def extract_features(
    url,
    return_diagnostics=False
):

    # --------------------------------------------------------
    # CLEAN URL
    # --------------------------------------------------------

    url = clean_url(url)

    # --------------------------------------------------------
    # URL FEATURES
    # --------------------------------------------------------

    url_features = extract_url_features(
        url
    )

    # --------------------------------------------------------
    # HTML FEATURES
    # --------------------------------------------------------

    html_features, diagnostics = (
        get_html_features(url)
    )

    # --------------------------------------------------------
    # COMBINE
    # --------------------------------------------------------

    features = {}

    features.update(
        url_features
    )

    features.update(
        html_features
    )

    # --------------------------------------------------------
    # EXACT 41 ORDER
    # --------------------------------------------------------

    values = []

    for name in FEATURE_NAMES:

        value = features.get(
            name,
            0.0
        )

        try:

            value = float(value)

        except (
            TypeError,
            ValueError
        ):

            value = 0.0

        values.append(value)

    result = pd.DataFrame(
        [values],
        columns=FEATURE_NAMES
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    if return_diagnostics:

        return result, diagnostics

    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_url = "https://www.uni-mainz.de"

    print()
    print("=" * 70)
    print("FEATURE EXTRACTOR TEST")
    print("=" * 70)

    print("URL:", test_url)

    X, diagnostics = extract_features(
        test_url,
        return_diagnostics=True
    )

    print()
    print(
        "FEATURE COUNT:",
        len(X.columns)
    )

    print()
    print(
        "FEATURE ORDER CORRECT:",
        X.columns.tolist()
        == FEATURE_NAMES
    )

    print()
    print(
        "ALL NUMERIC:",
        all(
            pd.api.types.is_numeric_dtype(
                dtype
            )
            for dtype in X.dtypes
        )
    )

    print()
    print(
        "HTML FETCH OK:",
        diagnostics["html_fetch_ok"]
    )

    print(
        "HTML STATUS:",
        diagnostics["html_status"]
    )

    print(
        "FINAL URL:",
        diagnostics["final_url"]
    )

    if diagnostics["error"]:

        print(
            "ERROR:",
            diagnostics["error"]
        )

    print()
    print("=" * 70)
    print("41 FEATURES")
    print("=" * 70)

    for name in FEATURE_NAMES:

        print(
            f"{name} = "
            f"{X.iloc[0][name]}"
        )

    print()
    print("=" * 70)
    print("TEST FINISHED")
    print("=" * 70)