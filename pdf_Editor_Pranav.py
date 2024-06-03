import streamlit as st
import PyPDF2
import os
import time
import io
from PyPDF2 import PdfReader, PdfWriter
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from PyPDF2 import PdfFileMerger, PdfFileReader
from PIL import Image
import gradio as gr
from pdf2docx import Converter
from docx import Document
from fpdf import FPDF
from streamlit_pdf_viewer import pdf_viewer
from PyPDF2 import PdfMerger

from spire.pdf.common import *
from spire.pdf import *

import base64
from streamlit.components.v1 import html

st.set_page_config(layout="wide")
st.markdown("""
<style>
    header {visibility: hidden;}
</style>
""",unsafe_allow_html=True)


video_html = """
		<style>
		#myVideo {
		  position: fixed;
		  right: 0;
		  bottom: 0;
		  min-width: 100%; 
		  min-height: 100%;
		  filter: brightness(70%); /* Adjust the brightness to make the video darker */
		}
		
		.content {
		  position: fixed;
		  bottom: 0;
		  background: rgba(255, 255, 255, 0.6); /* Adjust the transparency as needed */
		  color: #f1f1f1;
		  width: 100%;
		  padding: 20px;
		}
	        
		</style>
		<video autoplay muted loop id="myVideo">
		  <source src="https://assets.mixkit.co/videos/22729/22729-720.mp4" type="video/mp4">
		  Your browser does not support HTML5 video.
		</video>
		"""

st.markdown(video_html, unsafe_allow_html=True)




st.header("Welcome to PDF Editor Tool!")



def intro():
    st.sidebar.success("Select option")
   

def mergePdf():
    st.markdown(f'# {list(page_names_to_funcs.keys())[4]}')
 

    uploaded_files = st.file_uploader("Upload all the pdf files", accept_multiple_files=True, type=['pdf'])
    if uploaded_files is not None:
        if st.button("Merge PDFs"):
                
            with st.spinner('Wait for it...'):
                time.sleep(2)
                st.success('Completed!')

            mergedObject = PdfMerger()

            for file in uploaded_files:
                mergedObject.append(file)

            mergedObject.write("mergedfilesoutput.pdf")
            col1, col2 =st.columns([0.4,0.6])
            with col2:
                pdf_viewer("mergedfilesoutput.pdf", height=800)
            with col1:
                with open(os.path.join("mergedfilesoutput.pdf"), "rb") as f:
                    PDFbyte = f.read()
                    st.download_button(label="Download merged pdf's", 
                        data=PDFbyte,
                        file_name="merged.pdf",
                        mime='application/octet-stream')


def otherfunctions():
    try:
        import os
        import sys
        import traceback
        from io import BytesIO
        from pypdf import PaperSize, PdfReader, PdfWriter, Transformation
        from pypdf.errors import FileNotDecryptedError
        from streamlit import session_state
        import utils

        VERSION = "0.3.1"

        PAGE_STR_HELP = """
        Format
        ------
        **all:** all pages  
        **2:** 2nd page  
        **1-3:** pages 1 to 3  
        **2,4:** pages 2 and 4  
        **1-3,5:** pages 1 to 3 and 5"""

        # ---------- INIT SESSION STATES ----------
        session_state["decrypted_filename"] = (
            None
            if "decrypted_filename" not in session_state
            else session_state["decrypted_filename"]
        )
        session_state["password"] = (
            "" if "password" not in session_state else session_state["password"]
        )
        session_state["is_encrypted"] = (
            False if "is_encrypted" not in session_state else session_state["is_encrypted"]
        )
        # ---------- SIDEBAR ----------
        with st.sidebar:
            with st.expander("Other Supported operations"):
                st.info(
                    "* Upload from disk/URL\n"
                    "* Preview content/metadata\n"
                    "* Extract images\n"
                    "* Add/remove password\n"
                    "* Rotate/resize PDF\n"
                    "* Reduce PDF size\n"
                )

            try:
                pdf, reader, session_state["password"], session_state["is_encrypted"] = (
                    utils.load_pdf(key="main")
                )

            except FileNotDecryptedError:
                pdf = "password_required"

        if pdf == "password_required":
            st.error("PDF is password protected. Please enter the password to proceed.")
        elif pdf:
            lcol, rcol = st.columns(2)

            with rcol.expander(label="️🖼️ Extract images"):
                if page_numbers_str := st.text_input(
                    "Pages to extract images from?",
                    placeholder="all",
                    help=PAGE_STR_HELP,
                    key="extract_image_pages",
                ).lower():
                    try:
                        images = utils.extract_images(reader, page_numbers_str)
                    except (IndexError, ValueError):
                        st.error("Specified pages don't exist. Check the format.", icon="⚠️")
                    else:
                        if images:
                            for data, name in images.items():
                                st.image(data, caption=name)
                        else:
                            st.info("No images found")

            with lcol.expander(
                f"🔐 {'Change' if session_state['is_encrypted'] else 'Add'} password"
            ):
                new_password = st.text_input(
                    "Enter password",
                    type="password",
                )

                algorithm = st.selectbox(
                    "Algorithm",
                    options=["RC4-40", "RC4-128", "AES-128", "AES-256-R5", "AES-256"],
                    index=3,
                    help="Use `RC4` for compatibility and `AES` for security",
                )

                filename = f"protected_{session_state['name']}"

                if st.button(
                    "🔒 Submit",
                    use_container_width=True,
                    disabled=(len(new_password) == 0),
                ):
                    with PdfWriter() as writer:
                        # Add all pages to the writer
                        for page in reader.pages:
                            writer.add_page(page)

                        # Add a password to the new PDF
                        writer.encrypt(new_password, algorithm=algorithm)

                        # Save the new PDF to a file
                        with open(filename, "wb") as f:
                            writer.write(f)

                if os.path.exists(filename):
                    st.download_button(
                        "⬇️ Download protected PDF",
                        data=open(filename, "rb"),
                        mime="application/pdf",
                        file_name=filename,
                        use_container_width=True,
                    )

            with rcol.expander("🔓 Remove password"):
                if reader.is_encrypted:
                    st.download_button(
                        "⬇️ Download unprotected PDF",
                        data=open(session_state["decrypted_filename"], "rb"),
                        mime="application/pdf",
                        file_name=session_state["decrypted_filename"],
                        use_container_width=True,
                    )
                else:
                    st.info("PDF does not have a password")

            with lcol.expander("🔃 Rotate PDF"):
                # TODO: Add password back to converted PDF if original was protected
                st.caption("Will remove password if present")
                angle = st.slider(
                    "Clockwise angle",
                    min_value=0,
                    max_value=360,
                    step=90,
                    format="%d°",
                )

                with PdfWriter() as writer:
                    for page in reader.pages:
                        writer.add_page(page)
                        writer.pages[-1].rotate(angle)

                    # TODO: Write to byte_stream
                    writer.write("rotated.pdf")

                    with open("rotated.pdf", "rb") as f:
                        pdf_viewer(f.read(), height=250, width=300)
                        st.download_button(
                            "⬇️ Download rotated PDF",
                            data=f,
                            mime="application/pdf",
                            file_name=f"{session_state['name'].rsplit('.')[0]}_rotated_{angle}.pdf",
                            use_container_width=True,
                        )

            with lcol.expander("↔ Resize/Scale PDF"):
                # TODO: Add password back to converted PDF if original was protected
                st.caption("Will remove password if present")
                new_size = st.selectbox(
                    "New size",
                    options={
                        attr: getattr(PaperSize, attr)
                        for attr in dir(PaperSize)
                        if not attr.startswith("__")
                        and not callable(getattr(PaperSize, attr))
                    },
                    index=4,
                    help="Changes will be apparant only on printing the PDF",
                )

                scale_content = st.slider(
                    "Scale content",
                    min_value=0.1,
                    max_value=2.0,
                    step=0.1,
                    value=1.0,
                    help="Scale content independently of the page size",
                    format="%fx",
                )

                with PdfWriter() as writer:
                    for page in reader.pages:
                        page.scale_to(
                            width=getattr(PaperSize, new_size).width,
                            height=getattr(PaperSize, new_size).height,
                        )
                        op = Transformation().scale(sx=scale_content, sy=scale_content)
                        page.add_transformation(op)
                        writer.add_page(page)

                    # TODO: Write to byte_stream
                    writer.write("scaled.pdf")

                    with open("scaled.pdf", "rb") as f:
                        st.caption("Content scaling preview")
                        pdf_viewer(f.read(), height=250, width=300)
                        st.download_button(
                            "⬇️ Download scaled PDF",
                            data=f,
                            mime="application/pdf",
                            file_name=f"{session_state['name'].rsplit('.')[0]}_scaled_{new_size}_{scale_content}x.pdf",
                            use_container_width=True,
                        )

            
            with rcol.expander("🤏 Reduce PDF size"):
                st.markdown("Coming soon...")
                # # TODO: Add password back to converted PDF if original was protected
                # st.caption("Will remove password if present")

                # pdf_small = pdf

                # lcol, mcol, rcol = st.columns(3)

                # with lcol:
                #     remove_duplication = st.checkbox(
                #         "Remove duplication",
                #         help="""
                #         Some PDF documents contain the same object multiple times.  
                #         For example, if an image appears three times in a PDF it could be embedded three times. 
                #         Or it can be embedded once and referenced twice.  
                #         **Note:** This option will not remove objects, rather it will use a reference to the original object for subsequent uses.
                #         """,
                #     )

                #     remove_images = st.checkbox(
                #         "Remove images",
                #         help="Remove images from the PDF. Will also remove duplication.",
                #     )

                #     if remove_images or remove_duplication:
                #         pdf_small = utils.remove_images(
                #             pdf,
                #             remove_images=remove_images,
                #             password=session_state.password,
                #         )

                #     if st.checkbox(
                #         "Reduce image quality",
                #         help="""
                #         Reduce the quality of images in the PDF. Will also remove duplication.  
                #         May not work for all cases.
                #         """,
                #         disabled=remove_images,
                #     ):
                #         quality = st.slider(
                #             "Quality",
                #             min_value=0,
                #             max_value=100,
                #             value=50,
                #             disabled=remove_images,
                #         )
                #         pdf_small = utils.reduce_image_quality(
                #             pdf_small,
                #             quality,
                #             password=session_state.password,
                #         )

                #     if st.checkbox(
                #         "Lossless compression",
                #         help="Compress PDF without losing quality",
                #     ):
                #         pdf_small = utils.compress_pdf(
                #             pdf_small, password=session_state.password
                #         )

                #     original_size = sys.getsizeof(pdf)
                #     reduced_size = sys.getsizeof(pdf_small)
                #     st.caption(
                #         f"Reduction: {100 - (reduced_size / original_size) * 100:.2f}%"
                #     )

                # with mcol:
                #     st.caption(f"Original size: {original_size / 1024:.2f} KB")
                #     # utils.preview_pdf(
                #     #     reader,
                #     #     pdf,
                #     #     key="other",
                #     #     password=session_state.password,
                #     # )
                # with rcol:
                #     st.caption(f"Reduced size: {reduced_size / 1024:.2f} KB")
                #     # utils.preview_pdf(
                #     #     PdfReader(BytesIO(pdf_small)),
                #     #     pdf_small,
                #     #     key="other",
                #     #     password=session_state.password,
                #     # )
                # st.download_button(
                #     "⬇️ Download smaller PDF",
                #     data=pdf_small,
                #     mime="application/pdf",
                #     file_name=f"{filename}_reduced.pdf",
                #     use_container_width=True,
                # )
        else:
            st.info("👈 Upload a PDF to start")

    except Exception as e:
        st.error(
            f"""The app has encountered an error:  
            `{e}`  
            please contact on linkedin profile. Check footer""",
            icon="🥺",
        )
        st.code(traceback.format_exc())


# closing the pdf file object 
def pdf2text():
    st.markdown(f'# {list(page_names_to_funcs.keys())[3]}')
    st.write("""Upload pdf and convert into Text""")
    
    uploaded_file = st.file_uploader("Choose a file")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    if uploaded_file:
        with st.sidebar:
            st.caption("PDF preview")
            binary_data = uploaded_file.getvalue()
            pdf_viewer(input=binary_data,height=400, width=300)

    
    if uploaded_file is not None:
        if st.button("Convert .pdf to .docx"):
                
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()
            cv = Converter(stream=bytes_data)
            out_stream = io.BytesIO()
            cv.convert(out_stream)
            cv.close()
            # Download the file
            btn = st.download_button(
                label="Download docx",
                data=out_stream.getvalue(),
                file_name="pdf2wordconverted.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )



def pdfTominer():
    st.markdown(f'# {list(page_names_to_funcs.keys())[1]}')
    st.write("""Upload pdf and convert into Text""")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    uploaded_miner = st.file_uploader('Choose your .pdf file', type="pdf")
    if uploaded_miner:
        with st.sidebar:
            st.caption("PDF preview")
            binary_data = uploaded_miner.getvalue()
            pdf_viewer(input=binary_data,height=400, width=300)

    if uploaded_miner is not None:
        if st.button("Convert to text"):
                
            with st.spinner('Wait for it...'):
                time.sleep(2)
                st.success('File uploaded!')
            # pdfFileObj = open(uploaded_file, 'rb') 
      
            output_string = StringIO()
        
            parser = PDFParser(uploaded_miner)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)

            st.write(output_string.getvalue())
            st.download_button('Download the text', output_string.getvalue())
import os

def pdf2split():
    st.markdown(f'# {list(page_names_to_funcs.keys())[2]}')
    st.write(
        """
        Split the pages of your PDF
	"""
    )
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")
    if uploaded_file:
        with st.spinner('Processing your pdf...'):
            time.sleep(2)
            st.success('File uploaded!')
            # pdfFileObj = open(uploaded_file, 'rb') 
            inputpdf = PdfReader(uploaded_file)
    col1, col2 = st.columns([1, 1])
    with col1:
        if uploaded_file is not None:
            st.markdown("<h3>Split the PDF File<br/> by Each Page</h3>", unsafe_allow_html=True)
            if st.button("Split Each Page"):


                for i in range(len(inputpdf.pages)):
                    output = PdfWriter()
                    output.add_page(inputpdf.pages[i])
                    with open(f"document-page{i+1}.pdf", "wb") as outputStream:
                        output.write(outputStream)
                    
                    with open(f"document-page{i+1}.pdf", "rb") as f:
                        PDFbyte = f.read()
                        
                        st.download_button(label=f"Download Split Page {i+1}", 
                            data=PDFbyte,
                            file_name=f"split_pdf_page_{i+1}.pdf",
                            mime='application/octet-stream')    

    with col2:
        if uploaded_file:
                st.markdown("<h3>Split the PDF File by Specific Page Ranges</h3>", unsafe_allow_html=True)
                st.write("Select the page range:")
                start_page = st.slider("Start Page", 1, len(inputpdf.pages), 1)
                end_page = st.slider("End Page", start_page, len(inputpdf.pages), len(inputpdf.pages))

                if st.button("Split PDF"):
                    # Save the uploaded PDF file to a temporary location
                    with open("temp_pdf.pdf", "wb") as f:
                        f.write(uploaded_file.getvalue())

                    # Create a PdfDocument object
                    pdf = PdfDocument()
                    # Load the PDF file from the temporary location
                    pdf.LoadFromFile("temp_pdf.pdf")

                    # Split the PDF file into a new PDF file containing the selected page range
                    pdf_range = PdfWriter()
                    for page_num in range(start_page, end_page + 1):
                        pdf_range.add_page(inputpdf.pages[page_num - 1])

                    # Save the split PDF file
                    pdf_range.write("split_pdf_range.pdf")

                    # Remove the temporary PDF file
                    os.remove("temp_pdf.pdf")

                    with open("split_pdf_range.pdf", "rb") as f:
                        PDFbyte_range = f.read()
                        
                        st.download_button(label=f"Download Split PDF Range", 
                            data=PDFbyte_range,
                            file_name=f"split_pdf_range.pdf",
                            mime='application/octet-stream')


page_names_to_funcs = {
    "Home Page": intro,
    "PDF to Full Text" : pdfTominer,
    "Split pdf" : pdf2split,

    "PDF to Word Document" : pdf2text,
    "Merge pdf's" : mergePdf,
    "Other PDF operations" : otherfunctions
}

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #00000080;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.header("Select the operation")

demo_name = st.sidebar.selectbox("Click for options", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()


footer = """
<style>
a:link, a:visited {
    color: White;
    background-color: transparent;
    text-decoration: underline;
}

a:hover, a:active {
    color: aqua;
    text-decoration: underline;
}

.footer {
    position: fixed;
    left: 0px;
    bottom: 0;
    width: 100%;
    height: 30px;
    background-color: #80808070;
    color: aqua;
    text-align: center;
    font-size: 20px; /* Adjust font size here */
}

.footer p {
    transition: all 0.3s ease-in-out;
}

.footer p:hover {
    transform: scale(1.1); /* Zoom effect */
}

@keyframes glow {
    0% { color: white; }
    50% { color: orange; }
    100% { color: orange; }
}

.footer p:hover {
    animation: glow 1s infinite alternate; /* Glow effect */
}
</style>
<div class="footer">
    <p>Developed by <a class="normal-font" href="https://www.linkedin.com/in/pranav-baviskar" target="_blank">Pranav Baviskar</a></p>
</div>
"""

st.write(footer, unsafe_allow_html=True)
