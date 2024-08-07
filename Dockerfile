FROM python:3.12

RUN apt-get update && \
    apt-get install -y \
        texlive-latex-recommended \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-bibtex-extra biber

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# keep the container running by some magic
ENTRYPOINT ["tail"]
CMD ["-f","/dev/null"]