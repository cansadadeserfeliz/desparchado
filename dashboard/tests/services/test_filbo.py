# Tests for dashboard.services.filbo._speaker_matches

from dashboard.services.filbo import _speaker_matches


def _record(filbo_name: str, canonical_name: str) -> dict[str, str]:
    return {'FILBO_NAME': filbo_name, 'CANONICAL_NAME': canonical_name}


# ---------------------------------------------------------------------------
# FILBO_NAME matches
# ---------------------------------------------------------------------------

def test_filbo_name_matches_in_participants():
    record = _record('Lina Botero', 'Carolina López')
    assert _speaker_matches(record, 'Lina Botero', '', '') is True


def test_filbo_name_matches_in_event_title():
    record = _record('Lina Botero', 'Carolina López')
    assert _speaker_matches(record, '', 'Conversación con Lina Botero', '') is True


def test_filbo_name_matches_in_event_description():
    record = _record('Lina Botero', 'Carolina López')
    result = _speaker_matches(record, '', '', 'Esta charla presenta a Lina Botero.')
    assert result is True


# ---------------------------------------------------------------------------
# CANONICAL_NAME matches
# ---------------------------------------------------------------------------

def test_canonical_name_matches_in_participants():
    record = _record('J. García', 'Jorge García')
    assert _speaker_matches(record, 'Jorge García', '', '') is True


def test_canonical_name_matches_in_event_title():
    record = _record('J. García', 'Jorge García')
    assert _speaker_matches(record, '', 'Diálogo con Jorge García', '') is True


def test_canonical_name_matches_in_event_description():
    record = _record('J. García', 'Jorge García')
    description = 'El autor Jorge García presentará su libro.'
    result = _speaker_matches(record, '', '', description)
    assert result is True


# ---------------------------------------------------------------------------
# Critical word-boundary case
# ---------------------------------------------------------------------------

def test_lina_botero_does_not_match_catalina_botero():
    """'Lina Botero' must NOT match when the text only contains 'Catalina Botero'."""
    record = _record('Lina Botero', 'Lina Botero')
    assert _speaker_matches(record, 'Catalina Botero', '', '') is False


def test_lina_botero_does_not_match_catalina_botero_in_title():
    record = _record('Lina Botero', 'Lina Botero')
    assert _speaker_matches(record, '', 'Charla con Catalina Botero', '') is False


def test_lina_botero_does_not_match_catalina_botero_in_description():
    record = _record('Lina Botero', 'Lina Botero')
    result = _speaker_matches(record, '', '', 'Presenta Catalina Botero esta noche.')
    assert result is False


# ---------------------------------------------------------------------------
# Case-insensitive matching
# ---------------------------------------------------------------------------

def test_match_is_case_insensitive_filbo_name_uppercase():
    record = _record('LINA BOTERO', 'Carolina López')
    assert _speaker_matches(record, 'Lina Botero', '', '') is True


def test_match_is_case_insensitive_participants_uppercase():
    record = _record('Lina Botero', 'Carolina López')
    assert _speaker_matches(record, 'LINA BOTERO', '', '') is True


def test_match_is_case_insensitive_mixed_case():
    record = _record('lina botero', 'carolina lópez')
    assert _speaker_matches(record, '', 'Lina Botero en FILBo', '') is True


# ---------------------------------------------------------------------------
# No match
# ---------------------------------------------------------------------------

def test_no_match_when_name_absent_from_all_fields():
    record = _record('Lina Botero', 'Carolina López')
    result = _speaker_matches(record, 'Juan Pérez', 'Otro evento', 'Sin relación.')
    assert result is False


def test_no_match_when_all_fields_empty():
    record = _record('Lina Botero', 'Carolina López')
    assert _speaker_matches(record, '', '', '') is False


# ---------------------------------------------------------------------------
# Boundary positions (start and end of text)
# ---------------------------------------------------------------------------

def test_match_when_name_at_start_of_participants():
    record = _record('Lina Botero', 'Carolina López')
    assert _speaker_matches(record, 'Lina Botero y otro autor', '', '') is True


def test_match_when_name_at_end_of_participants():
    record = _record('Lina Botero', 'Carolina López')
    assert _speaker_matches(record, 'Presenta: Lina Botero', '', '') is True


def test_match_when_name_is_entire_participants_string():
    record = _record('Lina Botero', 'Carolina López')
    assert _speaker_matches(record, 'Lina Botero', '', '') is True


def test_match_when_canonical_name_at_start_of_description():
    record = _record('X', 'Jorge García')
    assert _speaker_matches(record, '', '', 'Jorge García abrirá el evento.') is True


def test_match_when_canonical_name_at_end_of_description():
    record = _record('X', 'Jorge García')
    assert _speaker_matches(record, '', '', 'El evento lo cierra Jorge García') is True


# ---------------------------------------------------------------------------
# Special characters in names (re.escape correctness)
# ---------------------------------------------------------------------------

def test_match_with_special_chars_in_filbo_name():
    """Names with regex-special characters like dots must be escaped correctly."""
    record = _record('J. García', 'Jorge García')
    # 'J. García' contains a literal dot — without re.escape it would match
    # any character in that position.
    assert _speaker_matches(record, 'J. García', '', '') is True


def test_dot_in_filbo_name_does_not_match_arbitrary_character():
    """The dot in 'J. García' must not act as a regex wildcard."""
    record = _record('J. García', 'Jorge García')
    # 'JX García' must not match; the dot must be literal.
    assert _speaker_matches(record, 'JX García', '', '') is False


# ---------------------------------------------------------------------------
# Either name suffices
# ---------------------------------------------------------------------------

def test_match_via_filbo_name_even_when_canonical_absent():
    record = _record('FilboAlias', 'CanonicalName')
    assert _speaker_matches(record, 'FilboAlias', '', '') is True


def test_match_via_canonical_name_even_when_filbo_absent():
    record = _record('FilboAlias', 'CanonicalName')
    assert _speaker_matches(record, 'CanonicalName', '', '') is True
