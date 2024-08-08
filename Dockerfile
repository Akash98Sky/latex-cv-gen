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

COPY schema.prisma .
RUN prisma generate

COPY . .

EXPOSE 80

# run the fastapi server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]