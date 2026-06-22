from foodbridge_agent.evals import main


def test_eval_fixture_suite_passes(capsys):
    main()

    captured = capsys.readouterr()
    assert "All FoodBridge eval fixtures passed." in captured.out

