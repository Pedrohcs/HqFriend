from src.domain.errors import FutureStateVersionError, StateRecoveredWarning


def test_aviso_de_recuperacao_informa_a_origem():
    from_backup = StateRecoveredWarning(restored_from_backup=True)
    from_scratch = StateRecoveredWarning(restored_from_backup=False)

    assert from_backup.restored_from_backup is True
    assert "backup" in str(from_backup)
    assert from_scratch.restored_from_backup is False
    assert "zero" in str(from_scratch)


def test_versao_futura_informa_a_versao_encontrada_e_a_suportada():
    # FEAT-15 / RNF02-CA6
    error = FutureStateVersionError(found="2.0", supported="1.1")

    assert (error.found, error.supported) == ("2.0", "1.1")
    assert "2.0" in str(error) and "1.1" in str(error)
