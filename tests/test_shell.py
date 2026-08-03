"""Tests for weatherlab.shell.handle_command - the parsing and
validation logic, which mostly doesn't touch the plotting window at
all. Only the actual _draw()/savefig() calls inside a successful
'plot'/'save' need a real window and are left untested here."""

from weatherlab.shell import ShellState, handle_command


def test_exit_returns_false():
    assert handle_command(ShellState(), "exit") is False


def test_quit_returns_false():
    assert handle_command(ShellState(), "quit") is False


def test_unrecognized_command_returns_true_and_does_not_crash():
    assert handle_command(ShellState(), "gibberish") is True


def test_help_prints_command_list(capsys):
    handle_command(ShellState(), "help")
    out = capsys.readouterr().out
    assert "set country" in out
    assert "set time" in out


def test_show_with_defaults_prints_not_set(capsys):
    handle_command(ShellState(), "show")
    out = capsys.readouterr().out
    assert "(not set)" in out
    assert "0.3" in out  # default min-radius


def test_show_after_setting_values_prints_them(capsys):
    state = ShellState()
    handle_command(state, "set country Bangladesh")
    handle_command(state, "show")
    assert "Bangladesh" in capsys.readouterr().out


def test_set_country_valid_name_updates_state():
    state = ShellState()
    handle_command(state, "set country Bangladesh")
    assert state.country == "Bangladesh"


def test_set_country_invalid_name_does_not_update_state():
    state = ShellState()
    handle_command(state, "set country NotARealCountry")
    assert state.country is None


def test_set_country_with_no_name_falls_through_to_unrecognized(capsys):
    state = ShellState()
    result = handle_command(state, "set country")
    assert result is True
    assert state.country is None
    assert "Unrecognized command" in capsys.readouterr().out


def test_set_time_valid_updates_state():
    state = ShellState()
    handle_command(state, "set time 2026-07-23 21:00")
    assert state.time == "2026-07-23 21:00"


def test_set_time_invalid_does_not_update_state():
    state = ShellState()
    handle_command(state, "set time not-a-time")
    assert state.time is None


def test_set_min_radius_valid_updates_state():
    state = ShellState()
    handle_command(state, "set min-radius 1.5")
    assert state.min_radius == 1.5


def test_set_min_radius_zero_is_allowed():
    state = ShellState()
    handle_command(state, "set min-radius 0")
    assert state.min_radius == 0.0


def test_set_min_radius_negative_is_rejected():
    state = ShellState()
    handle_command(state, "set min-radius -1")
    assert state.min_radius == 0.3  # unchanged from default


def test_set_min_radius_non_numeric_is_rejected():
    state = ShellState()
    handle_command(state, "set min-radius abc")
    assert state.min_radius == 0.3  # unchanged from default


def test_plot_with_nothing_set_does_not_crash_or_draw():
    state = ShellState()
    assert handle_command(state, "plot") is True
    assert state.has_plotted is False


def test_save_before_plotting_does_not_crash():
    state = ShellState()
    assert handle_command(state, "save") is True
    assert state.has_plotted is False
