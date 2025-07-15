import streamlit as st
from PIL import Image
import os
from io import StringIO

BACKGROUND_PATH = "background6.png"
START_SOUND = "begin.wav"
NO_ENCOUNTER_SOUND = "gallop.mp3"
CHEER_SOUND = "cheer.wav"
BOO_SOUND = "boo.mp3"

# Explicit full file-to-name mapping
PAWN_LABELS = {
    "BloxLeft.png": "Player Two, The Brothers Blox",
    "BloxRight.png": "Player One, The Brothers Blox",
    "FazLeft.png": "Player Two, Lord Fazworth",
    "FazRight.png": "Player One, Lord Fazworth",
    "MessiLeft.png": "Player Two, King Messi the GOAT",
    "MessiRight.png": "Player One, King Messi the GOAT",
    "MiniLeft.png": "Player Two, Lady Mini",
    "MiniRight.png": "Player One, Lady Mini",
    "PsyLeft.png": "Player Two, Sir Psyduck",
    "PsyRight.png": "Player One, Sir Psyduck",
    "ZombieLeft.png": "Player Two, Phone Zombies",
    "ZombieRight.png": "Player One, Phone Zombies"
}

st.title("⚔️ Joust Game Prototype")

# List valid pawns in directory
available_files = os.listdir(".")

player1_options = [f for f in available_files if f.endswith("Right.png") and f in PAWN_LABELS]
player2_options = [f for f in available_files if f.endswith("Left.png") and f in PAWN_LABELS]

if not player1_options or not player2_options:
    st.error("Missing expected pawn image files in root directory.")
    st.stop()

player1_display = st.sidebar.selectbox("Choose Player 1 Pawn (top path)", [PAWN_LABELS[f] for f in player1_options])
player2_display = st.sidebar.selectbox("Choose Player 2 Pawn (bottom path)", [PAWN_LABELS[f] for f in player2_options])

# Reverse mapping from display to file
rev_labels = {v: k for k, v in PAWN_LABELS.items()}
player1_pawn_file = rev_labels[player1_display]
player2_pawn_file = rev_labels[player2_display]

background = Image.open(BACKGROUND_PATH).convert("RGBA")
player1_pawn = Image.open(player1_pawn_file).convert("RGBA")
player2_pawn = Image.open(player2_pawn_file).convert("RGBA")

bottom_positions = [(20, 100), (100, 180), (180, 260), (260, 340), (340, 420), (420, 500)]
top_positions = [(420, 20), (340, 100), (260, 180), (180, 260), (100, 340), (20, 420)]

if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.p1_numbers = []
    st.session_state.p2_numbers = []
    st.session_state.results = []
    st.session_state.encounter = False
    st.session_state.p1_pos = 0
    st.session_state.p2_pos = 0
    st.session_state.round = 0

if st.session_state.step == 0:
    st.subheader("Player 1: Enter your numbers (1, 2, 3)")
    st.audio(START_SOUND)
    p1_input = st.multiselect("Choose your 3 numbers:", [1, 2, 3], key="p1_select")
    if len(p1_input) == 3:
        if st.button("Lock In Player 1 Numbers"):
            st.session_state.p1_numbers = p1_input.copy()
            st.session_state.step = 1
            st.rerun()

elif st.session_state.step == 1:
    st.subheader("Player 2: Enter your numbers (1, 2, 3)")
    p2_input = st.multiselect("Choose your 3 numbers:", [1, 2, 3], key="p2_select")
    if len(p2_input) == 3:
        if st.button("Lock In Player 2 Numbers"):
            st.session_state.p2_numbers = p2_input.copy()
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    round = st.session_state.round
    if round < 3:
        p1_move = st.session_state.p1_numbers[round]
        p2_move = st.session_state.p2_numbers[round]
        st.session_state.p1_pos += p1_move
        st.session_state.p2_pos += p2_move

        frame = background.copy()
        frame.paste(player1_pawn, top_positions[min(st.session_state.p1_pos, 5)], player1_pawn)
        frame.paste(player2_pawn, bottom_positions[min(st.session_state.p2_pos, 5)], player2_pawn)
        st.image(frame, caption=f"Round {round + 1}", use_column_width=True)

        st.session_state.results.append((p1_move, p2_move, st.session_state.p1_pos, st.session_state.p2_pos))

        if st.session_state.p1_pos + st.session_state.p2_pos >= 6:
            st.session_state.encounter = True
            st.session_state.step = 3
        elif round < 2:
            if st.button("Next Round"):
                st.session_state.round += 1
                st.rerun()
        else:
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.subheader("Final Result")
    final = background.copy()
    final.paste(player1_pawn, top_positions[min(st.session_state.p1_pos, 5)], player1_pawn)
    final.paste(player2_pawn, bottom_positions[min(st.session_state.p2_pos, 5)], player2_pawn)
    st.image(final, caption="Final Positions", use_column_width=True)

    last_round = st.session_state.results[-1]
    p1_move, p2_move = last_round[0], last_round[1]
    result_text = ""

    if st.session_state.encounter:
        if p1_move > p2_move:
            result_text = "🏆 Player 1 wins the encounter!"
            st.audio(CHEER_SOUND)
        elif p2_move > p1_move:
            result_text = "🏆 Player 2 wins the encounter!"
            st.audio(CHEER_SOUND)
        else:
            result_text = "🤝 It's a draw!"
            st.audio(BOO_SOUND)
        st.toast(result_text, icon="⚔️")
        st.info(f"Encounter occurred!\n\nLast round:\nPlayer 1 played {p1_move}, Player 2 played {p2_move}.")
    else:
        st.audio(NO_ENCOUNTER_SOUND)
        st.warning("Game ended without an encounter.")

    st.subheader("Round Summary")
    summary = StringIO()
    summary.write(f"Player 1 Pawn: {player1_display}\n")
    summary.write(f"Player 2 Pawn: {player2_display}\n")
    summary.write(f"Player 1 Numbers: {st.session_state.p1_numbers}\n")
    summary.write(f"Player 2 Numbers: {st.session_state.p2_numbers}\n\n")
    for i, (p1, p2, pos1, pos2) in enumerate(st.session_state.results, 1):
        summary.write(f"Round {i}: Player 1 → {p1} (pos {pos1}), Player 2 → {p2} (pos {pos2})\n")
    summary.write("\n")
    summary.write(f"Final Result: {result_text or 'No encounter'}\n")
    st.download_button("Download Game Log", data=summary.getvalue(), file_name="joust_game_log.txt")

    if st.button("Play Again"):
        for key in ["step", "p1_numbers", "p2_numbers", "results", "encounter", "p1_pos", "p2_pos", "round"]:
            st.session_state[key] = 0 if key in ["step", "round", "p1_pos", "p2_pos"] else [] if "numbers" in key or "results" in key else False
        st.rerun()
