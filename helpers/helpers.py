def generate_initials(name: str) -> str:
    """Generate initials from a name."""
    name_parts = name.split()
    if len(name_parts) == 1:
        # Single name: use the first 3 letters
        initials = name_parts[0][:3].upper()
    else:
        # Multiple names: use the first letter of each part
        initials = "".join(part[0].upper() for part in name_parts)
    # Ensure initials do not exceed 4 characters
    return initials[:4]
