import streamlit as st
import tempfile
import subprocess
import os

st.set_page_config(
    page_title="AVI → MP4 변환기",
    page_icon="🎬",
    layout="centered"
)

st.title("AVI → MP4 변환기")
st.caption("AVI 파일을 업로드하면 MP4로 변환합니다.")

uploaded_file = st.file_uploader(
    "AVI 파일을 선택하세요",
    type=["avi"]
)

if uploaded_file is not None:

    file_size = uploaded_file.size / 1024 / 1024

    st.info(
        f"파일명: {uploaded_file.name}\n\n"
        f"파일 크기: {file_size:.2f} MB"
    )

    if st.button(
        "MP4로 변환",
        type="primary",
        use_container_width=True
    ):

        input_path = None
        output_path = None

        try:

            progress = st.progress(0)
            status = st.empty()

            status.text("AVI 파일 준비 중...")
            progress.progress(10)

            # 임시 AVI 파일
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".avi"
            ) as input_file:

                input_file.write(
                    uploaded_file.getbuffer()
                )

                input_path = input_file.name

            # 임시 MP4 파일
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as output_file:

                output_path = output_file.name

            progress.progress(20)
            status.text("MP4로 변환 중...")

            command = [
                "ffmpeg",

                "-y",

                "-i",
                input_path,

                "-c:v",
                "libx264",

                "-preset",
                "fast",

                "-crf",
                "23",

                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-movflags",
                "+faststart",

                output_path
            ]

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode != 0:

                raise RuntimeError(
                    result.stderr.decode(
                        "utf-8",
                        errors="ignore"
                    )
                )

            progress.progress(90)
            status.text("MP4 파일 생성 중...")

            with open(
                output_path,
                "rb"
            ) as file:

                mp4_data = file.read()

            progress.progress(100)
            status.text("변환 완료!")

            st.success("MP4 변환이 완료되었습니다.")

            # 미리보기
            st.video(mp4_data)

            original_name = os.path.splitext(
                uploaded_file.name
            )[0]

            st.download_button(
                label="MP4 다운로드",
                data=mp4_data,
                file_name=f"{original_name}.mp4",
                mime="video/mp4",
                use_container_width=True
            )

        except Exception as e:

            st.error("변환 중 오류가 발생했습니다.")

            with st.expander("오류 내용"):
                st.code(str(e))

        finally:

            if (
                input_path
                and os.path.exists(input_path)
            ):
                os.remove(input_path)

            if (
                output_path
                and os.path.exists(output_path)
            ):
                os.remove(output_path)
