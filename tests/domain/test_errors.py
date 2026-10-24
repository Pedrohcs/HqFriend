from src.domain.errors import StateRecoveredWarning


def test_aviso_de_recuperacao_informa_a_origem():
    from_backup = StateRecoveredWarning(restored_from_backup=True)
    from_scratch = StateRecoveredWarning(restored_from_backup=False)

    assert from_backup.restored_from_backup is True
    assert "backup" in str(from_backup)
    assert from_scratch.restored_from_backup is False
    assert "zero" in str(from_scratch)
