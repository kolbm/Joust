import streamlit as st
from PIL import Image
import os
import time
from io import StringIO

# Set up paths
ASSET_DIR = "assets"
PAWN_DIR = os.path.join(ASSET_DIR, "pawns")
BACKGROUND_PATH = os.path.join(ASSET_DIR, "background6.png")

# Sound files (assumed to be in root directory)
START_SOUND = "begin.wav"
NO_ENCOUNTER_SOUND = "gallop.mp3"
CHEER_SOUND = "cheer.wav"
BOO_SOUND = "boo.mp3"

st.title("⚔️ Joust Game Prototype")

# Persistent session state
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.p1_numbers = []
    st.session_state.p2_numbers = []
    st.session_state.results = []
    st.session_state.encounter = False
    st.session_state.p1_pos = 0
    st.session_state.p2_pos = 0

pawn_options = sorted(set(f[:-9] for f in os.listdir(PAWN_DIR) if f.endswith("Left.png")))

# Select pawns
player1_name = st.sidebar.selectbox("Choose Player 1 Pawn (bottom path)", pawn_options, index=0)
player2_name = st.sidebar.selectbox("Choose Player 2 Pawn (top path)", pawn_options, index=1)

player1_pawn_file = f"{player1_name}Left.png"
player2_pawn_file = f"{player2_name}Right.png"

background = Image.open(BACKGROUND_PATH).convert("RGBA")
player1_pawn = Image.open(os.path.join(PAWN_DIR, player1_pawn_file)).convert("RGBA")
player2_pawn = Image.open(os.path.join(PAWN_DIR, player2_pawn_file)).convert("RGBA")

bottom_positions = [(20, 100), (100, 180), (180, 260), (260, 340), (340, 420), (420, 500)]
top_positions = [(420, 20), (340, 100), (260, 180), (180, 260), (100, 340), (20, 420)]

# Step 0: Player 1 input
if st.session_state.step == 0:
    st.subheader("Player 1: Enter your numbers (1, 2, 3)")
    st.audio(START_SOUND)
    p1_input = st.multiselect("Choose your 3 numbers:", [1, 2, 3], key="p1_select")
    if len(p1_input) == 3:
        if st.button("Lock In Player 1 Numbers"):
            st.session_state.p1_numbers = p1_input.copy()
            st.session_state.step = 1
            st.rerun()

# Step 1: Player 2 input
elif st.session_state.step == 1:
    st.subheader("Player 2: Enter your numbers (1, 2, 3)")
    p2_input = st.multiselect("Choose your 3 numbers:", [1, 2, 3], key="p2_select")
    if len(p2_input) == 3:
        if st.button("Lock In Player 2 Numbers"):
            st.session_state.p2_numbers = p2_input.copy()
            st.session_state.step = 2
            st.rerun()

# Step 2: Animate the game
elif st.session_state.step == 2:
    st.subheader("Game Progress")
    p1_pos = 0
    p2_pos = 0
    encounter = False
    results = []
    background_base = background.copy()

    for i in range(3):
        p1_move = st.session_state.p1_numbers[i]
        p2_move = st.session_state.p2_numbers[i]
        p1_pos += p1_move
        p2_pos += p2_move

        results.append((p1_move, p2_move, p1_pos, p2_pos))

        frame = background_base.copy()
        frame.paste(player1_pawn, bottom_positions[min(p1_pos, 5)], player1_pawn)
        frame.paste(player2_pawn, top_positions[min(p2_pos, 5)], player2_pawn)
        st.image(frame, caption=f"Round {i+1}", use_column_width=True)
        time.sleep(1.5)

        if p1_pos + p2_pos >= 6:
            encounter = True
            break

    st.session_state.results = results
    st.session_state.encounter = encounter
    st.session_state.p1_pos = p1_pos
    st.session_state.p2_pos = p2_pos
    st.session_state.step = 3
    st.rerun()

# Step 3: Show result
elif st.session_state.step == 3:
    st.subheader("Final Result")
    final = background.copy()
    final.paste(player1_pawn, bottom_positions[min(st.session_state.p1_pos, 5)], player1_pawn)
    final.paste(player2_pawn, top_positions[min(st.session_state.p2_pos, 5)], player2_pawn)
    st.image(final, caption="Final Positions", use_column_width=True)

    last_round = st.session_state.results[len(st.session_state.results) - 1]
    p1_move = last_round[0]
    p2_move = last_round[1]

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
    summary.write(f"Player 1 Pawn: {player1_name}\n")
    summary.write(f"Player 2 Pawn: {player2_name}\n")
    summary.write(f"Player 1 Numbers: {st.session_state.p1_numbers}\n")
    summary.write(f"Player 2 Numbers: {st.session_state.p2_numbers}\n\n")
    for i, (p1, p2, pos1, pos2) in enumerate(st.session_state.results, 1):
        summary.write(f"Round {i}: Player 1 → {p1} (pos {pos1}), Player 2 → {p2} (pos {pos2})\n")
    summary.write("\n")
    summary.write(f"Final Result: {result_text or 'No encounter'}\n")
    st.download_button("Download Game Log", data=summary.getvalue(), file_name="joust_game_log.txt")

    if st.button("Play Again"):
        for key in ["step", "p1_numbers", "p2_numbers", "results", "encounter", "p1_pos", "p2_pos"]:
            st.session_state[key] = 0 if key == "step" else [] if "numbers" in key or "results" in key else False
        st.rerun()
