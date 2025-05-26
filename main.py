# main_analyzer_app.py
import streamlit as st
import json as json_parser
from app.prompts.prompt_generator import (
    construct_overall_assignment_analysis_prompt_v3,
)  # Your existing import
from app.core.llm import gemini, chutes  # Your existing imports
from app.core.llm.llm_factory import get_llm_api_call_function
import asyncio  # Your existing import
from datetime import datetime, timezone  # For default timestamp
import re  # For regex operations
import json # For json.dumps and json.JSONDecodeError
import ast  # For ast.literal_eval


# --- NEW: Robust Cleaning Function ---
# --- NEW: Robust Cleaning Function (Revised) ---
def clean_llm_json_response(raw_response_str: str) -> str:
    """
    Cleans the raw string response from an LLM to extract and sanitize the JSON part.
    Handles <think>...</think> blocks, Markdown code fences,
    and attempts to fix common "relaxed JSON" issues like single quotes or Python literals.
    """
    if not isinstance(raw_response_str, str):
        # Assuming st is Streamlit, available in the context of your app
        # import streamlit as st # Uncomment if st is not globally available
        # st.warning("Input untuk pembersihan bukan string, mengembalikan apa adanya.")
        return raw_response_str

    cleaned_str = raw_response_str

    # 1. Remove <think>...</think> block if present at the beginning
    think_start_tag = "<think>"
    think_end_tag = "</think>"
    if cleaned_str.lstrip().startswith(think_start_tag):
        think_end_index = cleaned_str.find(think_end_tag)
        if think_end_index != -1:
            cleaned_str = cleaned_str[think_end_index + len(think_end_tag) :]
    cleaned_str = cleaned_str.strip()

    # 2. Remove Markdown code block fences (```json ... ``` or ``` ... ```)
    if cleaned_str.startswith("```json"):
        cleaned_str = cleaned_str[len("```json") :]
    elif cleaned_str.startswith("```"):
        cleaned_str = cleaned_str[len("```") :]
    if cleaned_str.endswith("```"):
        cleaned_str = cleaned_str[: -len("```")]
    cleaned_str = cleaned_str.strip()

    # If the string is empty after initial cleaning, return it.
    if not cleaned_str:
        return cleaned_str

    # Attempt 1: Try parsing with ast.literal_eval (for Python-like structures)
    # This handles single quotes for keys/strings, None, True, False naturally.
    try:
        # ast.literal_eval expects a string that's a valid Python literal.
        # It doesn't like raw newlines in simple strings unless they are triple-quoted.
        # However, LLMs might produce them. If ast.literal_eval is very sensitive,
        # specific pre-processing for it might be needed, or rely on its failure
        # to fall through to regex methods.
        python_obj = ast.literal_eval(cleaned_str)
        # If successful, convert the Python object to a valid JSON string.
        # json.dumps will ensure double quotes, handle None->null, True->true, False->false,
        # and correctly escape special characters including newlines within strings.
        return json.dumps(python_obj, ensure_ascii=False) # ensure_ascii=False for non-latin chars
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as e:
        # ast.literal_eval failed, proceed to regex-based cleaning for JSON.
        # print(f"INFO: ast.literal_eval failed: {e}. Falling back to regex JSON cleaning.") # For debugging
        pass

    # Attempt 2: Regex-based cleaning to make it JSON-compliant
    # (This is the fallback if ast.literal_eval fails)

    #   a. Convert Python's None, True, False to JSON's null, true, false
    #      Use word boundaries to avoid replacing "None" within a word.
    cleaned_str = re.sub(r"\bNone\b", "null", cleaned_str)
    cleaned_str = re.sub(r"\bTrue\b", "true", cleaned_str)
    cleaned_str = re.sub(r"\bFalse\b", "false", cleaned_str)

    #   b. Fix single-quoted keys to double-quoted keys: e.g., 'key': -> "key":
    #      This pattern looks for a character that can precede a key ({, [, ,, or whitespace),
    #      followed by a single-quoted key, then a colon.
    cleaned_str = re.sub(r"([{[(,\s])'([a-zA-Z_][a-zA-Z0-9_]*)'\s*:", r'\1"\2":', cleaned_str)

    #   c. Attempt to fix single-quoted string *values*. This is more complex.
    #      This pattern looks for "key": 'value' and tries to change it to "key": "value".
    #      It handles \' inside the single-quoted value by converting it to ' in the new double-quoted value.
    #      Pattern: ("key_already_double_quoted"\s*:\s*) ' (content of single quoted value, group 3) '
    #                                       group 1 |                               group 3 |
    value_pattern = r'("(?:\\["\\]|[^\n"\\])*"\s*:\s*)\'((?:\\\'|[^\'])*)\''
    
    def replace_single_quoted_val(match):
        key_part = match.group(1) # e.g., "mykey":
        single_quoted_content = match.group(2) # Content like 'it\\\'s text'
        
        # Unescape \' to ' for the new double-quoted string
        content_unescaped_single_quotes = single_quoted_content.replace("\\'", "'")
        # Escape any actual " characters that might now be in the content
        final_content = content_unescaped_single_quotes.replace('"', '\\"')
        return f'{key_part}"{final_content}"'

    # Iteratively apply value replacement as regex might not catch all in one pass with complex inputs
    for _ in range(5): # Limit iterations to prevent infinite loops
        new_cleaned_str = re.sub(value_pattern, replace_single_quoted_val, cleaned_str)
        if new_cleaned_str == cleaned_str:
            break
        cleaned_str = new_cleaned_str
        
    #   d. Remove trailing commas before closing braces or brackets
    cleaned_str = re.sub(r",\s*([}\]])", r"\1", cleaned_str)

    #   e. Escape unescaped newlines *within string values* to `\\n`.
    #      This was step 4 in your original code. It's crucial for valid JSON strings.
    #      It should ideally run after quotes are fixed.
    #      This regex replaces a newline character `\n` that is NOT preceded by a backslash `\`
    #      with an escaped newline `\\n`.
    cleaned_str = re.sub(r"(?<!\\)\n", r"\\n", cleaned_str)
    
    #   f. (Optional but can help) Ensure special characters within strings are escaped.
    #      The most common ones are handled by json.dumps if ast.literal_eval worked.
    #      If we are in the regex path, backslashes and double quotes within strings
    #      must be escaped. The value_pattern above tries to handle this for values.
    #      This is tricky to do universally with regex if not already done.

    return cleaned_str


# --- Main Streamlit App ---
def run_streamlit_app():
    """
    Sets up and runs the Streamlit application for AI Assignment Analyzer.
    This page handles input and AI call.
    """
    st.set_page_config(page_title="Penganalisis Tugas AI (V3)", layout="wide")

    # Initialize session state
    if "analysis_results_data" not in st.session_state:
        st.session_state.analysis_results_data = None
    if "raw_analysis_response_str" not in st.session_state:
        st.session_state.raw_analysis_response_str = None
    if "questions_data" not in st.session_state:
        st.session_state.questions_data = [
            {
                "question_id": "Q1",
                "question_text": "",
                "student_answer_text": "",
                "lecturer_answer_text": "",
                "rubric": "",
                "rubric_max_score": 10,
            }
        ]
    if "generated_prompt" not in st.session_state:
        st.session_state.generated_prompt = None

    st.title("📝 Penganalisis Tugas AI (V3)")
    st.markdown("---")
    st.info(
        """
    **Petunjuk:**
    1.  Isi semua detail tugas di bawah ini. Setiap pertanyaan memerlukan rubrik dan skor maksimalnya sendiri.
    2.  Pilih Model AI yang ingin Anda gunakan.
    3.  Klik tombol "Analisis Tugas".
    4.  Model AI akan mengevaluasi jawaban mahasiswa dan memberikan umpan balik di halaman hasil terpisah.
    """
    )
    st.markdown("---")

    st.sidebar.header("🤖 Pilihan Model AI")
    selected_model = st.sidebar.radio(
        "Pilih model AI yang akan digunakan untuk analisis:",
        ("Gemini", "Chutes", "Azure"),
        key="model_selection",
    )
    st.sidebar.markdown(f"Anda telah memilih: **{selected_model}**")
    st.sidebar.markdown("---")
    # Ganti dengan path logo Anda jika ada, atau biarkan placeholder
    st.sidebar.image(
        "https://i.ytimg.com/vi/eXwZMAz9Vh8/maxresdefault.jpg", caption="EduAI"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.header("1. Detail Tugas")
        assignment_id = st.text_input(
            "Masukkan ID Tugas:",
            key="assignment_id",
            placeholder="contoh: EKOMAKRO_UTS_GENAP2024",
        )
        student_id = st.text_input(
            "Masukkan ID Mahasiswa:",
            key="student_id",
            placeholder="contoh: MHS12345678",
        )
        overall_assignment_title = st.text_input(
            "Judul Keseluruhan Tugas (Opsional):",
            key="overall_assignment_title",
            placeholder="contoh: Ujian Tengah Semester Ekonomi Makro - Musim Semi 2024",
        )
        lecturer_overall_notes = st.text_area(
            "Catatan/Panduan Umum Dosen (Opsional):",
            height=100,
            key="lecturer_overall_notes",
            placeholder="contoh: Menilai pemahaman keseluruhan konsep fundamental.",
        )

    with col2:
        st.header("2. Pertanyaan, Jawaban & Rubrik per Pertanyaan")
        st.markdown(
            "Tambahkan pertanyaan, jawaban mahasiswa, jawaban ideal dosen, dan rubrik spesifik untuk setiap pertanyaan."
        )
        for i, qa_pair in enumerate(st.session_state.questions_data):
            st.subheader(f"Pertanyaan {i+1}")
            qa_pair["question_id"] = st.text_input(
                f"ID Pertanyaan {i+1}:",
                value=qa_pair.get("question_id", f"Q{i+1}"),
                key=f"question_id_{i}",
            )
            qa_pair["question_text"] = st.text_area(
                f"Teks Pertanyaan {i+1}:",
                value=qa_pair.get("question_text", ""),
                height=100,
                key=f"question_text_{i}",
                placeholder="Masukkan teks Pertanyaan lengkap di sini.",
            )
            qa_pair["lecturer_answer_text"] = st.text_area(
                f"Jawaban Ideal Dosen untuk Pertanyaan {i+1}:",
                value=qa_pair.get("lecturer_answer_text", ""),
                height=120,
                key=f"lecturer_answer_{i}",
                placeholder="Berikan jawaban model yang komprehensif atau poin-poin kunci terperinci untuk pertanyaan ini.",
            )
            qa_pair["student_answer_text"] = st.text_area(
                f"Jawaban Mahasiswa untuk Pertanyaan {i+1}:",
                value=qa_pair.get("student_answer_text", ""),
                height=120,
                key=f"student_answer_{i}",
                placeholder="Tempelkan jawaban lengkap mahasiswa untuk pertanyaan ini di sini.",
            )
            qa_pair["rubric"] = st.text_area(
                f"Rubrik untuk Pertanyaan {i+1}:",
                value=qa_pair.get("rubric", ""),
                height=100,
                key=f"question_rubric_{i}",
                placeholder="Deskripsikan rubrik untuk pertanyaan spesifik ini (misalnya, Akurasi definisi; Kejelasan penjelasan).",
            )
            qa_pair["rubric_max_score"] = st.number_input(
                f"Skor Maksimum untuk Rubrik Pertanyaan {i+1}:",
                min_value=1,  # Skor max biasanya > 0
                value=qa_pair.get("rubric_max_score", 10),
                key=f"question_rubric_max_score_{i}",
            )
            if st.button(f"Hapus Pertanyaan {i+1}", key=f"remove_question_{i}"):
                st.session_state.questions_data.pop(i)
                st.rerun()
            st.markdown("---")
        if st.button("➕ Tambah Pertanyaan Baru", key="add_question_button"):
            st.session_state.questions_data.append(
                {
                    "question_id": f"Q{len(st.session_state.questions_data) + 1}",
                    "question_text": "",
                    "student_answer_text": "",
                    "lecturer_answer_text": "",
                    "rubric": "",
                    "rubric_max_score": 10,
                }
            )
            st.rerun()

    st.markdown("---")
    st.header("3. Analisis Tugas dengan Model AI")

    if st.button("🚀 Analisis Tugas", key="analyze_button", type="primary"):
        st.session_state.analysis_results_data = None
        st.session_state.raw_analysis_response_str = None
        st.session_state.generated_prompt = None

        # Validasi
        if not assignment_id or not student_id:
            st.error("⚠️ Harap masukkan ID Tugas dan ID Mahasiswa.")
            return
        if not st.session_state.questions_data:
            st.error("⚠️ Harap tambahkan setidaknya satu pertanyaan.")
            return
        valid_questions = True
        for i, q in enumerate(st.session_state.questions_data):
            if not q.get("question_text") or not q.get("student_answer_text"):
                st.error(
                    f"⚠️ Pertanyaan {i+1}: Harap pastikan teks pertanyaan dan jawaban mahasiswa disediakan."
                )
                valid_questions = False
            if not q.get("rubric"):
                st.error(f"⚠️ Pertanyaan {i+1}: Harap berikan deskripsi rubrik.")
                valid_questions = False
            if q.get("rubric_max_score", 0) <= 0:
                st.error(
                    f"⚠️ Pertanyaan {i+1}: Skor maksimum untuk rubrik harus lebih besar dari 0."
                )
                valid_questions = False
        if not valid_questions:
            return

        st.info(
            f"⏳ Membuat prompt dan memanggil model **{selected_model}**... Harap tunggu."
        )
        try:
            questions_and_answers_for_prompt = []
            for qa_pair in st.session_state.questions_data:
                q_data = {
                    "question_id": qa_pair["question_id"],
                    "question_text": qa_pair["question_text"],
                    "student_answer_text": qa_pair["student_answer_text"],
                    "lecturer_answer_text": qa_pair.get(
                        "lecturer_answer_text", "*Tidak Ada Jawaban Dosen Disediakan*"
                    ),
                    "rubric": qa_pair["rubric"],
                    "rubric_max_score": qa_pair["rubric_max_score"],
                }
                questions_and_answers_for_prompt.append(q_data)

            full_prompt = construct_overall_assignment_analysis_prompt_v3(
                assignment_id=assignment_id,
                student_id=student_id,
                questions_and_answers=questions_and_answers_for_prompt,
                overall_assignment_title=overall_assignment_title or None,
                lecturer_overall_notes=lecturer_overall_notes or None,
            )
            st.session_state.generated_prompt = full_prompt

            api_response_raw = None
            with st.spinner(
                f"🤖 Memanggil model {selected_model}... Ini mungkin memakan waktu sebentar."
            ):
                try:
                    llm_api_call_function = get_llm_api_call_function(selected_model)
                    api_response_raw = llm_api_call_function(full_prompt)
                except ValueError as ve:
                    st.error(f"❌ Kesalahan konfigurasi model: {ve}")
                    return
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan saat memanggil model {selected_model}: {e}")
                    return

            if api_response_raw:
                st.session_state.raw_analysis_response_str = api_response_raw

                # --- Gunakan fungsi pembersihan yang baru ---
                cleaned_json_str = clean_llm_json_response(api_response_raw)

                if not cleaned_json_str:  # Jika string kosong setelah dibersihkan
                    st.error(
                        "❌ Respons AI kosong atau tidak valid setelah dibersihkan."
                    )
                    st.session_state.analysis_results_data = None
                    return

                try:
                    parsed_json_response = json_parser.loads(cleaned_json_str)

                    # Pastikan field penting ada di JSON, tambahkan jika tidak ada
                    # Ini penting untuk konsistensi data di halaman hasil
                    if "student_identifier" not in parsed_json_response:
                        parsed_json_response["student_identifier"] = student_id
                    if "assignment_identifier" not in parsed_json_response:
                        parsed_json_response["assignment_identifier"] = assignment_id
                    if "submission_timestamp_utc" not in parsed_json_response:
                        # Anda mungkin ingin menggunakan timestamp yang lebih akurat dari input pengguna jika ada
                        parsed_json_response["submission_timestamp_utc"] = datetime.now(
                            timezone.utc
                        ).isoformat()
                    # Pastikan 'question_identifier' ada jika formatnya tetap
                    if "question_identifier" not in parsed_json_response:
                        parsed_json_response["question_identifier"] = (
                            "overall_assignment"  # Default
                        )

                    st.session_state.analysis_results_data = parsed_json_response
                    st.success(
                        f"✅ Analisis selesai menggunakan {selected_model}! Mengalihkan ke halaman hasil..."
                    )
                    st.switch_page("pages/1_📊_Analysis_Result.py")
                except json_parser.JSONDecodeError as json_err:
                    st.error(
                        f"❌ Kesalahan mengurai respons AI sebagai JSON setelah dibersihkan: {json_err}"
                    )
                    st.error(
                        f"Konten yang dicoba untuk diurai: '{cleaned_json_str[:200]}...' (maks 200 karakter pertama)"
                    )  # Tampilkan sebagian kecil untuk debug
                    st.error(
                        "Harap periksa respons mentah di bawah ini. Halaman hasil tidak dapat ditampilkan."
                    )
                    st.session_state.analysis_results_data = None
            else:
                st.error(
                    f"❌ Tidak ada respons yang diterima dari model {selected_model} atau terjadi kesalahan selama panggilan API."
                )
                st.session_state.raw_analysis_response_str = (
                    "Kesalahan: Tidak ada respons atau panggilan API gagal."
                )
                st.session_state.analysis_results_data = None
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan aplikasi: {e}")
            st.exception(e)
            st.session_state.raw_analysis_response_str = (
                f"Terjadi kesalahan aplikasi: {str(e)}"
            )
            st.session_state.analysis_results_data = None

    if st.session_state.generated_prompt:
        with st.expander(
            "🔍 Lihat Prompt yang Dihasilkan yang Dikirim ke AI", expanded=False
        ):
            st.text_area(
                "Prompt:",
                value=st.session_state.generated_prompt,
                height=300,
                disabled=True,
                key="generated_prompt_display_area",
            )

    if (
        st.session_state.raw_analysis_response_str
        and not st.session_state.analysis_results_data
    ):
        st.markdown("---")
        st.subheader(f"📜 Respons Mentah Model AI ({selected_model}):")
        st.text_area(
            "Respons Mentah:",
            value=st.session_state.raw_analysis_response_str,
            height=400,
            disabled=True,
        )
        st.markdown("---")


if __name__ == "__main__":
    run_streamlit_app()
