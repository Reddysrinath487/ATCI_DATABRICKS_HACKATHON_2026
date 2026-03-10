import streamlit as st
from datetime import datetime, timezone
import os
import time
import traceback
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import SubmitTask, NotebookTask

# -------------------------------
# CONFIG
# -------------------------------
VOLUME_PATH = "/Volumes/atci_databricks_hackathon_2025/atci_clinical_transcript_ai_hackathon/raw_data/Bot_Uploaded_Files"
notebook_path="/Workspace/ATCI_CLINICAL_TRANSCRIPT_AI_HACKATHON/Notebooks/Clincal_Transcript_AI_Pipeline"
w = WorkspaceClient()

st.set_page_config(
    page_title="Clinical Transcript AI Assistant",
    page_icon="🏥",
    layout="centered"
)

# -------------------------------
# UI STYLING (Clinical Theme)
# -------------------------------
st.markdown("""
<style>
    .main {
        background-color: #f7fbff;
    }
    .upload-box {
        border: 2px dashed #4a90e2;
        padding: 25px;
        border-radius: 10px;
        background-color: #ffffff;
    }
    .success-box {
        background-color: #e6fffa;
        padding: 15px;
        border-radius: 8px;
        border-left: 6px solid #38b2ac;
    }
    .title-text {
        color: #2b6cb0;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1 class='title-text'>🏥 Clinical Transcript Extraction</h1>", unsafe_allow_html=True)
st.write("Upload clinical PDF documents to securely store them in Unity Catalog for AI-based extraction.")

st.divider()

# -------------------------------
# FILE UPLOAD
# -------------------------------
st.markdown("<div class='upload-box'>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📄 Upload Clinical PDF Files",
    type=["pdf"],
    help="Upload visit notes, discharge summaries, or clinical transcripts"
)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# SAVE TO UNITY CATALOG
# -------------------------------
if uploaded_file is not None and "uploaded_pdf_path" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    datestamp = datetime.now().strftime("%Y-%m-%d")
    # Split filename + extension
    filename, ext = os.path.splitext(uploaded_file.name)
    # Clean filename
    safe_filename = filename.replace(" ", "_")
    # Folder inside Volume
    folder_path = f"{VOLUME_PATH}"
    # Rebuild final path (explicitly add .pdf back)
    save_path = f"{folder_path}/{safe_filename}_{timestamp}.pdf"

    try:
        w.files.upload(
            file_path=save_path,
            contents=uploaded_file.getvalue(),
            overwrite=True
        )

        st.markdown(
            f"""
            <div class='success-box'>
                ✅ <b>Upload Successful!</b><br>
                File saved securely in Unity Catalog.<br><br>
                <b>Path:</b><br>
                <code>{save_path}</code>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.session_state["uploaded_pdf_path"] = save_path

    except Exception as e:
        st.error(f"❌ Failed to save file: {str(e)}")

datestamp = datetime.now().strftime("%Y-%m-%d")
job_param = f"{VOLUME_PATH}"
JOB_ID = '516186285440893'

st.divider()
if st.button("Run Notebook Now"):
    with st.spinner("Triggering notebook..."):
        try:
            run = w.jobs.run_now(
                job_id=JOB_ID,
                notebook_params={
                    "src_folder": job_param   # must match your job parameter name
                }
            )
            st.success(f"Job triggered successfully! Run ID: {run.run_id}")
            # Wait until job finishes
            while True:
                run_status = w.jobs.get_run(run_id=run.run_id)
                life_cycle = run_status.state.life_cycle_state.value
                if life_cycle in ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]:
                    break
                time.sleep(10)
            result_state = run_status.state.result_state.value if run_status.state.result_state else None
            st.link_button(
                "View Job Run",
                f"{w.config.host}/#job/{JOB_ID}/run/{run.run_id}"
            )
            if result_state == "SUCCESS":
                st.success("🎉 Clinical extraction completed successfully, Loaded Into Final Table")
            else:
                st.error(f"❌ Job failed with result: {result_state}")
        except Exception as e:
            st.error(f"Error: {e}\n\n{traceback.format_exc()}")
# -------------------------------
# FOOTER PLACEHOLDER
# -------------------------------
st.divider()
st.markdown(
    """
    <div style="color:gray; font-size:12px; text-align:center;">
        © Clinical Transcript AI Assistant
        <hr style="margin:4px 0; border:0; border-top:1px solid #ddd;">
        Powered by Accenture & Databricks Business Group
    </div>
    """,
    unsafe_allow_html=True
)
