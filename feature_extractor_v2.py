
import re
import urllib.parse
import ipaddress

import pandas as pd
import tldextract
import joblib
import requests
from bs4 import BeautifulSoup


# ============================================================
# EXACT 41 FEATURES USED BY THE TRAINED MODEL
# ============================================================

FEATURE_NAMES = [
    'URLLength',
    'DomainLength',
    'IsDomainIP',
    'TLDLength',
    'NoOfSubDomain',
    'HasObfuscation',
    'NoOfObfuscatedChar',
    'ObfuscationRatio',
    'NoOfLettersInURL',
    'LetterRatioInURL',
    'NoOfDegitsInURL',
    'DegitRatioInURL',
    'NoOfEqualsInURL',
    'NoOfQMarkInURL',
    'NoOfAmpersandInURL',
    'NoOfOtherSpecialCharsInURL',
    'SpacialCharRatioInURL',
    'IsHTTPS',
    'LineOfCode',
    'LargestLineLength',
    'HasTitle',
    'HasFavicon',
    'Robots',
    'IsResponsive',
    'NoOfURLRedirect',
    'NoOfSelfRedirect',
    'HasDescription',
    'NoOfPopup',
    'NoOfiFrame',
    'HasExternalFormSubmit',
    'HasSocialNet',
    'HasSubmitButton',
    'HasHiddenFields',
    'HasPasswordField',
    'HasCopyrightInfo',
    'NoOfImage',
    'NoOfCSS',
    'NoOfJS',
    'NoOfSelfRef',
    'NoOfEmptyRef',
    'NoOfExternalRef'
]


# ============================================================
# HTML / WEBPAGE FEATURES
# ============================================================

def get_html_features(url):

    features = {}

    try:

        response = requests.get(
            url,
            timeout=5,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            allow_redirects=True
        )

        html = response.text

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # ----------------------------------------------------
        # HTML lines
        # ----------------------------------------------------

        lines = html.split("\n")

        features["LineOfCode"] = len(lines)

        features["LargestLineLength"] = max(
            [len(line) for line in lines],
            default=0
        )

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        features["HasTitle"] = (
            1 if soup.find("title") else 0
        )

        # ----------------------------------------------------
        # Description
        # ----------------------------------------------------

        features["HasDescription"] = (
            1
            if soup.find(
                "meta",
                attrs={
                    "name": re.compile(
                        "^description$",
                        re.I
                    )
                }
            )
            else 0
        )

        # ----------------------------------------------------
        # Favicon
        # ----------------------------------------------------

        features["HasFavicon"] = (
            1
            if soup.find(
                "link",
                rel=lambda value:
                    value and (
                        "icon" in value
                        if isinstance(value, str)
                        else "icon" in value
                    )
            )
            else 0
        )

        # ----------------------------------------------------
        # Images
        # ----------------------------------------------------

        features["NoOfImage"] = len(
            soup.find_all("img")
        )

        # ----------------------------------------------------
        # CSS
        # ----------------------------------------------------

        features["NoOfCSS"] = len(
            soup.find_all(
                "link",
                rel=lambda value:
                    value and (
                        "stylesheet" in value
                        if isinstance(value, str)
                        else "stylesheet" in value
                    )
            )
        )

        # ----------------------------------------------------
        # JavaScript
        # ----------------------------------------------------

        features["NoOfJS"] = len(
            soup.find_all("script")
        )

        # ----------------------------------------------------
        # iframe
        # ----------------------------------------------------

        features["NoOfiFrame"] = len(
            soup.find_all("iframe")
        )

        # ----------------------------------------------------
        # External form submission
        # ----------------------------------------------------

        features["HasExternalFormSubmit"] = 0

        page_domain = urllib.parse.urlparse(
            response.url
        ).hostname

        for form in soup.find_all("form"):

            action = form.get(
                "action",
                ""
            ).strip()

            if not action:
                continue

            absolute_action = urllib.parse.urljoin(
                response.url,
                action
            )

            action_domain = urllib.parse.urlparse(
                absolute_action
            ).hostname

            if (
                action_domain
                and page_domain
                and action_domain.lower()
                != page_domain.lower()
            ):
                features["HasExternalFormSubmit"] = 1
                break

        # ----------------------------------------------------
        # Password field
        # ----------------------------------------------------

        features["HasPasswordField"] = (
            1
            if soup.find(
                "input",
                attrs={
                    "type": re.compile(
                        "^password$",
                        re.I
                    )
                }
            )
            else 0
        )

        # ----------------------------------------------------
        # Submit button
        # ----------------------------------------------------

        features["HasSubmitButton"] = (
            1
            if soup.find(
                ["button", "input"],
                attrs={
                    "type": re.compile(
                        "^submit$",
                        re.I
                    )
                }
            )
            else 0
        )

        # ----------------------------------------------------
        # Hidden fields
        # ----------------------------------------------------

        features["HasHiddenFields"] = (
            1
            if soup.find(
                "input",
                attrs={
                    "type": re.compile(
                        "^hidden$",
                        re.I
                    )
                }
            )
            else 0
        )

        # ----------------------------------------------------
        # Popups
        # ----------------------------------------------------

        popup_patterns = [
            "window.open",
            "alert(",
            "prompt(",
            "confirm("
        ]

        html_lower = html.lower()

        features["NoOfPopup"] = sum(
            html_lower.count(pattern)
            for pattern in popup_patterns
        )

        # ----------------------------------------------------
        # Social networks
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

        features["HasSocialNet"] = 0

        for social in social_domains:

            if social in html_lower:
                features["HasSocialNet"] = 1
                break

        # ----------------------------------------------------
        # Copyright
        # ----------------------------------------------------

        features["HasCopyrightInfo"] = (
            1
            if "copyright" in html_lower
            or "©" in html
            else 0
        )

        # ----------------------------------------------------
        # Robots
        # ----------------------------------------------------

        robots_url = urllib.parse.urljoin(
            response.url,
            "/robots.txt"
        )

        try:

            robots_response = requests.get(
                robots_url,
                timeout=3,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            features["Robots"] = (
                1
                if robots_response.status_code == 200
                else 0
            )

        except Exception:

            features["Robots"] = 0

        # ----------------------------------------------------
        # Responsive
        # ----------------------------------------------------

        viewport = soup.find(
            "meta",
            attrs={
                "name": re.compile(
                    "^viewport$",
                    re.I
                )
            }
        )

        features["IsResponsive"] = (
            1 if viewport else 0
        )

        # ----------------------------------------------------
        # Links
        # ----------------------------------------------------

        links = soup.find_all(
            "a",
            href=True
        )

        external = 0
        self_ref = 0
        empty = 0

        current_domain = urllib.parse.urlparse(
            response.url
        ).hostname

        for link in links:

            href = link.get(
                "href",
                ""
            ).strip()

            if href in [
                "",
                "#",
                "javascript:void(0)",
                "javascript:void(0);"
            ]:
                empty += 1
                continue

            absolute_url = urllib.parse.urljoin(
                response.url,
                href
            )

            link_domain = urllib.parse.urlparse(
                absolute_url
            ).hostname

            if not link_domain:

                self_ref += 1

            elif (
                current_domain
                and link_domain.lower()
                == current_domain.lower()
            ):

                self_ref += 1

            else:

                external += 1

        features["NoOfExternalRef"] = external
        features["NoOfSelfRef"] = self_ref
        features["NoOfEmptyRef"] = empty

        # ----------------------------------------------------
        # Redirects
        # ----------------------------------------------------

        features["NoOfURLRedirect"] = len(
            response.history
        )

        features["NoOfSelfRedirect"] = 0

        for redirect in response.history:

            old_domain = urllib.parse.urlparse(
                redirect.url
            ).hostname

            location = redirect.headers.get(
                "Location",
                ""
            )

            new_url = urllib.parse.urljoin(
                redirect.url,
                location
            )

            new_domain = urllib.parse.urlparse(
                new_url
            ).hostname

            if (
                old_domain
                and new_domain
                and old_domain.lower()
                == new_domain.lower()
            ):
                features["NoOfSelfRedirect"] += 1

    except Exception:
        pass

    return features


# ============================================================
# URL FEATURE EXTRACTION
# ============================================================

def extract_features(url):

    features = {}

    url = url.strip()

    if not re.match(
        r"^[a-zA-Z][a-zA-Z0-9+.-]*://",
        url
    ):
        url = "http://" + url

    parsed = urllib.parse.urlparse(url)

    domain = parsed.hostname or ""

    # --------------------------------------------------------
    # URL length
    # --------------------------------------------------------

    features["URLLength"] = len(url)

    # --------------------------------------------------------
    # Domain length
    # --------------------------------------------------------

    features["DomainLength"] = len(domain)

    # --------------------------------------------------------
    # IP address
    # --------------------------------------------------------

    try:

        ipaddress.ip_address(domain)

        features["IsDomainIP"] = 1

    except ValueError:

        features["IsDomainIP"] = 0

    # --------------------------------------------------------
    # HTTPS
    # --------------------------------------------------------

    features["IsHTTPS"] = (
        1
        if parsed.scheme.lower() == "https"
        else 0
    )

    # --------------------------------------------------------
    # TLD
    # --------------------------------------------------------

    ext = tldextract.extract(url)

    features["TLDLength"] = len(
        ext.suffix
    )

    # --------------------------------------------------------
    # Subdomains
    # --------------------------------------------------------

    if ext.subdomain:

        features["NoOfSubDomain"] = len(
            ext.subdomain.split(".")
        )

    else:

        features["NoOfSubDomain"] = 0

    # --------------------------------------------------------
    # Letters
    # --------------------------------------------------------

    letters = len(
        re.findall(
            r"[A-Za-z]",
            url
        )
    )

    features["NoOfLettersInURL"] = letters

    features["LetterRatioInURL"] = (
        letters / len(url)
        if len(url)
        else 0
    )

    # --------------------------------------------------------
    # Digits
    # --------------------------------------------------------

    digits = len(
        re.findall(
            r"[0-9]",
            url
        )
    )

    features["NoOfDegitsInURL"] = digits

    features["DegitRatioInURL"] = (
        digits / len(url)
        if len(url)
        else 0
    )

    # --------------------------------------------------------
    # Query characters
    # --------------------------------------------------------

    features["NoOfEqualsInURL"] = url.count("=")

    features["NoOfQMarkInURL"] = url.count("?")

    features["NoOfAmpersandInURL"] = url.count("&")

    # --------------------------------------------------------
    # Special characters
    # --------------------------------------------------------

    special = len(
        re.findall(
            r"[^A-Za-z0-9]",
            url
        )
    )

    features["NoOfOtherSpecialCharsInURL"] = special

    features["SpacialCharRatioInURL"] = (
        special / len(url)
        if len(url)
        else 0
    )

    # --------------------------------------------------------
    # Obfuscation
    # --------------------------------------------------------

    obfuscated_chars = len(
        re.findall(
            r"%[0-9A-Fa-f]{2}",
            url
        )
    )

    features["NoOfObfuscatedChar"] = (
        obfuscated_chars
    )

    features["HasObfuscation"] = (
        1
        if obfuscated_chars > 0
        else 0
    )

    features["ObfuscationRatio"] = (
        obfuscated_chars / len(url)
        if len(url)
        else 0
    )

    # --------------------------------------------------------
    # Webpage features
    # --------------------------------------------------------

    html_features = get_html_features(url)

    features.update(html_features)

    # --------------------------------------------------------
    # Make sure EXACTLY the 41 trained features exist
    # --------------------------------------------------------

    final_features = {}

    for name in FEATURE_NAMES:

        final_features[name] = features.get(
            name,
            0
        )

    # --------------------------------------------------------
    # Create DataFrame in EXACT model order
    # --------------------------------------------------------

    result = pd.DataFrame(
        [[
            final_features[name]
            for name in FEATURE_NAMES
        ]],
        columns=FEATURE_NAMES
    )

    return result
