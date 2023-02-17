"""
Main UI driver for project

Author: Conor Carmichael
"""
import sys, os

sys.path.append(os.getcwd())


from src.theory import *
from src.settings import dev_mode
from src.ui.display import *
from src.ui.state_mgmt import *

# from time import time
import streamlit as st
from copy import deepcopy

check_and_init_state()

st.set_page_config(layout="wide")

page_title = ":musical_score: Create Your Chord Progressions "

st.title(page_title)
project_settings_container = st.container()
chord_disp_container = st.container()


# ****************************************** #
#                 Run Display
# ****************************************** #
set_sidebar()
display_song(get_state_val("song"), get_state_val("current_progression"))

# Input where all chords shown as option
with st.container():
    show_progression_controls()


with st.container():
    if get_state_val("input_method").upper() == "FREE":
        # Handle chord input according to input method
        chord_input_form(
            root_options=notes_list.get_notes(),
            root_fmt_fn=lambda note: note.name if not note is None else note,
            chord_type_options=[chord for chord in ChordType],
            chord_type_fmt_fn=lambda chord_type: " ".join(chord_type.name.split("_")).title(),
            inversion_range=inversion_values,
            submit_fn=submit_chord_to_prog
        )

    elif get_state_val("input_method").upper() == "TEXT":
        st.markdown("Text input is a work in progress", unsafe_allow_html=True)

    else:
        scale_factory, scale_root, scale_mode = scale_selection()

        set_state_val("scale_type", scale_factory)
        set_state_val("scale_mode", scale_mode)
        set_state_val("scale_root", scale_root)

        # Get the appopriate scale type give the base scale and mode choices
        set_state_val(
            "scale_type",
            get_state_val("scale_type").get_mode_definition(
                mode_name=get_state_val("scale_mode")
            )
            if not get_state_val("scale_mode") is None
            else scale_factory,
        )

        scale = get_state_val("scale_type").generate_scale(
            root_note=get_state_val("scale_root")
        )
        set_state_val("scale", scale)

        if get_state_val("input_method").upper() == "GENERIC":

            chord_input_form(
                [i + 1 for i in range(len(scale))][:-1],
                None,
                [chord for chord in ChordType],
                lambda chord_type: " ".join(chord_type.name.split("_")).title()
                if not chord_type is None
                else chord_type,
                inversion_values,
                submit_generic_chord_to_prog,
            )

        elif get_state_val("input_method").upper() == "DIATONIC":
            st.markdown("Diatonic input is a work in progress", unsafe_allow_html=True)
