import json # Hanya dibutuhkan untuk pemformatan string JSON contoh dalam prompt

# --- DATA DEMO (sebagaimana disediakan oleh pengguna, sedikit disesuaikan untuk konsistensi) ---
# 1. assignment_id
demo_assignment_id = "KIM101_UTS_S24" # Contoh: ID Tugas Kimia

# 2. student_id
demo_student_id = "SISWA_007"

# 3. questions_and_answers
demo_questions_and_answers = [
    {
        "question_id": "KIM101_P1",
        "question_text": "Definisikan 'mol' dalam kimia dan jelaskan signifikansinya dengan bilangan Avogadro.",
        "student_answer_text": "Mol itu seperti lusin, tapi untuk atom. Itu adalah sejumlah partikel tertentu, yaitu bilangan Avogadro, 6.022 x 10^23. Ini signifikan karena memungkinkan kita menimbang atom dan molekul dengan menghubungkan satuan massa atom ke gram.",
        "lecturer_answer_text": "Mol adalah satuan dalam kimia yang mewakili 6.022 x 10^23 partikel, atom, atau molekul. Ini memungkinkan ahli kimia untuk menghitung partikel dengan menimbangnya. Bilangan Avogadro sangat penting karena menyediakan jembatan antara skala atomik dan kuantitas makroskopis.",
        "rubric":"Akurasi definisi, relevansi dengan bilangan Avogadro, kejelasan penjelasan", # Contoh rubrik deskriptif
        "rubric_max_score": 10
    },
    {
        "question_id": "KIM101_P2",
        "question_text": "Jelaskan perbedaan antara ikatan ionik dan ikatan kovalen. Berikan contoh untuk masing-masing.",
        "student_answer_text": "Ikatan ionik adalah ketika atom memberi atau mengambil elektron, seperti NaCl di mana Na memberi elektron ke Cl. Ikatan kovalen adalah ketika atom berbagi elektron, seperti dalam H2O di mana oksigen berbagi elektron dengan dua hidrogen. Ikatan ionik antara logam dan nonlogam, kovalen biasanya antara nonlogam.",
        "lecturer_answer_text": "Ikatan ionik dihasilkan dari daya tarik elektrostatik antara ion-ion yang berlawanan muatan, terbentuk melalui transfer lengkap satu atau lebih elektron dari logam ke nonlogam (misalnya, NaCl). Ikatan kovalen melibatkan pembagian pasangan elektron antara dua atom nonlogam untuk mencapai konfigurasi elektron yang stabil (misalnya, H2O). Perbedaan utama termasuk sifat keterlibatan elektron (transfer vs. berbagi) dan jenis unsur yang biasanya terlibat.",
        "rubric": "Akurasi deskripsi ikatan ionik; Akurasi deskripsi ikatan kovalen; Kebenaran contoh; Kejelasan diferensiasi",
        "rubric_max_score": 8
    },
    {
        "question_id": "KIM101_P3",
        "question_text": "Setarakan persamaan kimia berikut: Fe + O2 -> Fe2O3",
        "student_answer_text": "4Fe + 3O2 -> 2Fe2O3. Saya memastikan ada 4 Fe di kedua sisi dan 6 O di kedua sisi.",
        "lecturer_answer_text": "Persamaan yang setara adalah 4Fe + 3O2 -> 2Fe2O3. Ini memastikan bahwa jumlah atom besi (4 di setiap sisi) dan atom oksigen (6 di setiap sisi) terjaga.",
        "rubric": "Kebenaran persamaan yang setara; Verifikasi keseimbangan atom",
        "rubric_max_score": 5
    }
]

# 4. overall_assignment_title (Opsional)
demo_overall_assignment_title = "Ujian Tengah Semester Kimia Dasar 1 - Semester Genap 2024"

# 5. lecturer_overall_notes (Opsional)
demo_lecturer_overall_notes = "Harap nilai pemahaman keseluruhan konsep-konsep fundamental. Untuk P3, proses penyetaraan sama pentingnya dengan jawaban akhir. Periksa apakah siswa memahami 'mengapa' di balik definisi mereka di P1 dan P2, bukan hanya hafalan. Dorong penjelasan terperinci yang menunjukkan pemahaman komponen rubrik untuk setiap pertanyaan."


def construct_overall_assignment_analysis_prompt_v3_bahasa(
    assignment_id: str,
    student_id: str,
    questions_and_answers: list[dict], # Setiap dict mencakup rubrik per pertanyaan, jawaban dosen, dll.
    overall_assignment_title: str | None = None,
    lecturer_overall_notes: str | None = None
) -> str:
    """
    Membuat prompt terperinci untuk analisis AI terhadap keseluruhan tugas (semua pertanyaan),
    menginstruksikan AI untuk mengembalikan evaluasi keseluruhan yang komprehensif dalam format JSON tertentu.
    Versi ini menekankan pemecahan rubrik per pertanyaan dan menghilangkan rubrik tugas keseluruhan.
    Dimodifikasi untuk DeepSeek guna mencegah tag <think> dan memastikan keluaran JSON yang bersih.

    Args:
        assignment_id (str): ID tugas keseluruhan.
        student_id (str): ID siswa.
        questions_and_answers (list[dict]): Daftar dictionary, di mana setiap dictionary
                                            berisi 'question_id', 'question_text',
                                            'student_answer_text', 'lecturer_answer_text',
                                            'rubric' (string deskriptif untuk pertanyaan tersebut),
                                            dan 'rubric_max_score'.
        overall_assignment_title (str, opsional): Judul tugas.
        lecturer_overall_notes (str, opsional): Catatan umum dari dosen tentang tugas tersebut.

    Returns:
        str: String prompt yang diformat.
    """

    questions_answers_formatted_for_prompt = ""
    total_possible_score_from_questions = 0
    for i, qa_pair in enumerate(questions_and_answers):
        q_id = qa_pair.get('question_id', f"p_{i+1}")
        q_text = qa_pair.get('question_text', '*T/A*') # T/A = Tidak Ada
        s_ans = qa_pair.get('student_answer_text', '*Tidak Ada Jawaban Diberikan*')
        lecturer_ans = qa_pair.get('lecturer_answer_text', '*Tidak Ada Jawaban Dosen Diberikan*')
        rubric = qa_pair.get('rubric', '*Tidak Ada Rubrik Diberikan*') # Ini adalah rubrik deskriptif untuk pertanyaan
        rubric_max_score = qa_pair.get('rubric_max_score', 0)
        total_possible_score_from_questions += rubric_max_score

        questions_answers_formatted_for_prompt += f"   Pertanyaan {i+1} (ID: {q_id}):\n"
        questions_answers_formatted_for_prompt += f"     Teks Pertanyaan:\n     ```\n     {q_text}\n     ```\n"
        questions_answers_formatted_for_prompt += f"     Jawaban Siswa:\n     ```\n     {s_ans}\n     ```\n"
        questions_answers_formatted_for_prompt += f"     Jawaban Model/Panduan Dosen:\n     ```\n     {lecturer_ans}\n     ```\n"
        questions_answers_formatted_for_prompt += f"     Rubrik untuk Pertanyaan Ini (Skor Maks: {rubric_max_score}):\n     ```\n     {rubric}\n     ```\n\n"

    lecturer_notes_formatted = lecturer_overall_notes if lecturer_overall_notes else "*T/A*"
    assignment_title_formatted = overall_assignment_title if overall_assignment_title else "*T/A*"

    # Contoh struktur JSON yang diperbarui dalam Bahasa Indonesia
    output_json_structure_example = {
      "id_penilaian": "id_unik_pelaksanaan_penilaian",
      "pengenal_siswa": student_id,
      "pengenal_tugas": assignment_id,
      "pengenal_pertanyaan": "tugas_keseluruhan",
      "stempel_waktu_pengumpulan_utc": "YYYY-MM-DDTHH:MM:SSZ", # Diisi AI
      "stempel_waktu_penilaian_utc": "YYYY-MM-DDTHH:MM:SSZ", # Diisi AI
      "penilaian_keseluruhan": {
        "skor": 0, # integer, jumlah skor dari penilaian_pertanyaan
        "skor_maksimum_mungkin": total_possible_score_from_questions, # jumlah rubric_max_score dari semua pertanyaan
        "ringkasan_kinerja": "...",
        "umpan_balik_positif_umum": "...",
        "area_perbaikan_umum": "...",
        "langkah_selanjutnya_atau_sumber_daya_yang_disarankan": ["...", "..."]
      },
      "penilaian_pertanyaan": [ # Array untuk penilaian pertanyaan individual
        {
            "id_pertanyaan": "PLACEHOLDER_ID_PERTANYAAN", # Diambil dari input
            "teks_pertanyaan": "...", # Diambil dari input
            "teks_jawaban_siswa": "...", # Diambil dari input
            "teks_jawaban_dosen": "...", # Diambil dari input
            "rubrik": "...", # Diambil dari input
            "skor_maks_rubrik": 0, # Diambil dari input
            "penilaian": {
                "skor": 0, # integer, diberikan oleh AI berdasarkan rubrik
                "skor_maksimum_mungkin": 0, # Sama dengan skor_maks_rubrik untuk pertanyaan ini
                "umpan_balik_komponen_rubrik": [ # BARU: Umpan balik terperinci per komponen rubrik
                    {
                        "deskripsi_komponen": "misalnya, Akurasi definisi",
                        "evaluasi_komponen": "Definisi siswa sebagian besar akurat tetapi melewatkan...",
                        "kekuatan_komponen": "...",
                        "area_perbaikan_komponen": "..."
                    }
                    # ... komponen lainnya jika tersirat dalam rubrik
                ],
                "umpan_balik_keseluruhan_pertanyaan": "Umpan balik umum untuk pertanyaan spesifik ini, merangkum kinerja komponen.",
                "poin_kunci_yang_dicakup_siswa": ["...", "..."], # Keseluruhan untuk pertanyaan
                "konsep_yang_hilang_dalam_jawaban_siswa": ["...", "..."] # Keseluruhan untuk pertanyaan
            }
        }
        # ... objek penilaian_pertanyaan lainnya
      ],
      "skor_kepercayaan_ai": {
        "kepercayaan_penilaian_keseluruhan": 0.0,
        "kepercayaan_pembuatan_umpan_balik": 0.0
      },
      "metadata_pemrosesan": {
        "model_yang_digunakan": "deepseek-chat", # atau model lain yang relevan
        "versi_prompt": "evalyn_prompt_keseluruhan_v3.0_deepseek_id"
      }
    }
    json_example_str = json.dumps(output_json_structure_example, indent=2, ensure_ascii=False) # ensure_ascii=False untuk karakter non-ASCII

    prompt = f"""Anda adalah Asisten Pengajar AI ahli untuk Evalyn. Tujuan utama Anda adalah menganalisis seluruh pengumpulan tugas siswa, yang terdiri dari jawaban atas beberapa pertanyaan. Untuk setiap pertanyaan, Anda akan mengevaluasi jawaban siswa berdasarkan rubrik per pertanyaan yang disediakan dan jawaban model dari dosen. Anda kemudian akan memberikan evaluasi keseluruhan yang komprehensif untuk seluruh tugas.

    **INSTRUKSI KELUARAN PENTING:**
    - JANGAN gunakan tag berpikir, blok penalaran, atau teks penjelasan apa pun
    - JANGAN sertakan <think>, <reasoning>, atau tag bergaya XML lainnya
    - Hanya RESPON dengan objek JSON yang diminta
    - Mulai respons Anda segera dengan kurung kurawal pembuka {{
    - Jangan tambahkan teks apa pun sebelum atau sesudah respons JSON

    **Konteks Tugas:**

    1.  **ID Tugas Keseluruhan:**
        `{assignment_id}`

    2.  **ID Siswa:**
        `{student_id}`

    3.  **Judul Tugas (Opsional):**
        `{assignment_title_formatted}`

    4.  **Catatan/Panduan Umum Dosen untuk Seluruh Tugas (Opsional):**
        ```
        {lecturer_notes_formatted}
        ```

    5.  **Pertanyaan Tugas, Jawaban Siswa, Jawaban Dosen, dan Rubrik Per Pertanyaan:**
        (Seluruh pengumpulan siswa dan semua detail yang relevan untuk setiap pertanyaan disediakan di bawah)
    {questions_answers_formatted_for_prompt}
    **Tugas AI dan Persyaratan Analisis:**

    Berdasarkan semua informasi di atas, lakukan analisis berikut dan kembalikan hasilnya sebagai satu objek JSON yang valid:

    1.  **Tinjauan Holistik:** Baca dan pahami semua pertanyaan, jawaban siswa, jawaban model dosen, dan rubrik per pertanyaan. Pertimbangkan catatan umum dosen jika disediakan.

    2.  **Penilaian Per Pertanyaan (Terperinci):**
        * Untuk SETIAP pertanyaan yang disediakan dalam input:
            * Analisis dengan cermat `teks_jawaban_siswa` dalam kaitannya dengan `teks_pertanyaan`, `teks_jawaban_dosen` (sebagai model/tolok ukur), dan yang paling penting, `rubrik` yang disediakan untuk pertanyaan tersebut.
            * **Rincian Komponen Rubrik:** Identifikasi komponen atau kriteria berbeda yang tersirat oleh string `rubrik` untuk pertanyaan tersebut. Misalnya, jika rubrik adalah "Akurasi definisi; Kejelasan penjelasan; Penggunaan contoh", ini adalah tiga komponen.
            * **Evaluasi Berdasarkan Komponen:** Untuk SETIAP komponen rubrik yang diidentifikasi:
                * Evaluasi seberapa baik `teks_jawaban_siswa` menangani komponen spesifik tersebut.
                * Catat kekuatan spesifik dan area untuk perbaikan untuk komponen tersebut, merujuk pada `teks_jawaban_dosen` jika relevan.
                * Isi array `umpan_balik_komponen_rubrik` dalam objek `penilaian` untuk pertanyaan tersebut. Setiap item dalam array ini harus merinci evaluasi Anda untuk satu komponen rubrik pertanyaan.
            * **Skor untuk Pertanyaan:** Berdasarkan evaluasi berbasis komponen Anda terhadap seluruh `rubrik` untuk pertanyaan tersebut, berikan `skor` hingga `skor_maks_rubrik`.
            * **Umpan Balik Keseluruhan Pertanyaan:** Berikan `umpan_balik_keseluruhan_pertanyaan` yang merangkum kinerja siswa pada pertanyaan spesifik ini.
            * Identifikasi `poin_kunci_yang_dicakup_siswa` dan `konsep_yang_hilang_dalam_jawaban_siswa` untuk pertanyaan secara keseluruhan.
            * Isi satu objek dalam array `penilaian_pertanyaan` dalam output JSON untuk setiap pertanyaan. Pastikan `id_pertanyaan`, `teks_pertanyaan`, `teks_jawaban_siswa`, `teks_jawaban_dosen`, `rubrik`, dan `skor_maks_rubrik` dalam output Anda cocok dengan input untuk pertanyaan tersebut. `penilaian.skor_maksimum_mungkin` harus sama dengan `skor_maks_rubrik`.

    3.  **Perhitungan Skor Tugas Keseluruhan:**
        * Hitung `penilaian_keseluruhan.skor`. Ini HARUS merupakan jumlah dari nilai `skor` dari SETIAP `penilaian_pertanyaan` individual.
        * `penilaian_keseluruhan.skor_maksimum_mungkin` HARUS merupakan jumlah dari semua nilai `skor_maks_rubrik` dari SETIAP `penilaian_pertanyaan`.

    4.  **Umpan Balik Keseluruhan yang Komprehensif untuk Seluruh Tugas:**
        * Berdasarkan kinerja siswa di semua pertanyaan, tulis `ringkasan_kinerja`.
        * Berikan `umpan_balik_positif_umum`.
        * Berikan `area_perbaikan_umum`.
        * Jika berlaku, daftar `langkah_selanjutnya_atau_sumber_daya_yang_disarankan`.
        * Isi objek `penilaian_keseluruhan` dalam JSON dengan informasi ini.

    5.  **Pengidentifikasi JSON dan Stempel Waktu:**
        * Isi `pengenal_siswa` dan `pengenal_tugas`.
        * Gunakan "tugas_keseluruhan" untuk `pengenal_pertanyaan` di root JSON.
        * Hasilkan stempel waktu UTC saat ini untuk `stempel_waktu_penilaian_utc`. Anda dapat menggunakan placeholder seperti "YYYY-MM-DDTHH:MM:SSZ" untuk `stempel_waktu_pengumpulan_utc` dan `stempel_waktu_penilaian_utc`, yang akan diisi oleh sistem.

    **Format Output JSON yang Diperlukan:**

    Kembalikan analisis lengkap Anda untuk **SELURUH TUGAS** sebagai satu objek JSON yang valid dengan struktur persis seperti ini:

    ```json
    {json_example_str}