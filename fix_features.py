import joblib

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

path = r"C:\Users\GANESAN\Documents\PROJECT\Phising detection system\model\feature_names.pkl"

joblib.dump(FEATURE_NAMES, path)

print("Feature file fixed.")
print("Feature count:", len(FEATURE_NAMES))
print("Saved to:", path)