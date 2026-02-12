"""Utility functions for company data cleaning and processing."""


def clean_display_name(name: str, country: str = None) -> str:
    """
    Clean and shorten a company display name by removing common suffixes and descriptors.

    Args:
        name: The company legal name to clean.
        country: Optional country code to apply country-specific cleaning rules (not implemented yet).
    Returns:
        The cleaned display name, stripped of trailing descriptors.
    """
    if not name or not isinstance(name, str):
        return name
    
    # Ordered list of separators to check (case-insensitive)
    # These are common business type indicators and descriptors in Croatian
    separators = [
        "j.d.o.o",                                          # Limited liability company
        "jednostavno društvo s ograničenom odgovornošću",   # Full form of limited liability company
        "d.o.o",                                            # Limited liability company (short form)
        "društvo sa ograničenom odgovornošću",              # Full form of limited liability company
        "društvo s ograničenom odgovornošću",               # Full form of limited liability company (alternative)
        "društvo s ograničenom odgovoronošću",              # Common misspelling
        "d.d",                                              # Joint-stock company
        "dioničko društvo",                                 # Full form of joint-stock company
        "građevinski obrt",                                 # Construction craft business
        "sezonski obrt",                                    # Seasonal craft business
        "soboslikarski obrt",                               # Painting craft business
        "ugostiteljski obrt",                               # Hospitality craft business
        "zajednički obrt",                                  # Joint craft business
        ",obrt",                                            # Craft business
        ", obrt",                                           # Craft business
        "obrt za",                                          # Craft business
        "pružatelj ugostiteljskih usluga",                  # Hospitality service provider
        "vl.",                                              # "vlasnik" - owner
        "vlasnik",                                          # Owner
        ",",                                                # Remove anything after a comma
        # "s.p.",                                             # Sole proprietor
        # "d.p.",                                             # General partnership
        # "i.p.",                                             # Individual entrepreneur
    ]
    
    # Strip leading/trailing whitespace
    cleaned = name.strip()
    
    # Iterate through separators and find the first occurrence
    for separator in separators:
        # Case-insensitive search
        index = cleaned.lower().find(separator.lower())
        
        if index == 0:
            continue

        if index != -1:
            # Extract the part before the separator
            cleaned = cleaned[:index].strip(" ,-")
            break
    
    return cleaned if cleaned else name
