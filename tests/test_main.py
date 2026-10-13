from practica_headliners import main


def test_main_se_ejecuta(capsys):
    main()
    assert "Hello from practica-headliners!" in capsys.readouterr().out