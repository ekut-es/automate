from automate import main


def test_main_version(capsys):
    "test that main is runnble"

    main.program.print_version()

    out, err = capsys.readouterr()

    for line in err:
        assert not line.startswith("ERROR")
        assert not line.startswith("WARNING")

    for line in out:
        print(line)
