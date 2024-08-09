# LaTeX CV Gen

## Install python packages
```shell
$ python3 -m pip install -r requirements.txt
```

## Run the cv-gen script
```shell
$ python3 cv-gen.py -p profile-data.yaml -i input
```
[Note: Replace `profile-data.yaml` with your data file path, and `input` with your input directory path of the tex files.]


## Syntax
### Value replacement
Use `${<field path>}` to replace the content with the value in that field.

e.g.

Input
```latex
\name{${name}}
\tagline{${tagline}}
```
Output
```latex
\name{Akash Mondal}
\tagline{Innovative software developer with a passion for solving complex problems and delivering creative solutions.}
```

### Repetitive content generation
Use `${# for <item name> in <iterator field path> #} ... ${<item name>} ... ${# endfor #}` to repeat the content over the iterator.

e.g.

Input
```latex
\cvsection[page1sidebar]{Experience}

${# for exp in work #}
\cvevent{${exp.position}$}{${exp.company}$}{${exp.date}$}{${exp.location}}
\begin{itemize}
${# for desc in exp.description #}
  \item ${desc}
${# endfor #}
\end{itemize}
\divider
\medskip
${# endfor #}
```
Output
```latex
\cvsection[page1sidebar]{Experience}

\cvevent{TDP Software Engineer$}{Optum$}{July 2022 - Present$}{Bangalore, India}
\begin{itemize}

\item Placeholder.
\item Placeholder.

\end{itemize}
\divider
\medskip
\cvevent{Software Developer Intern$}{Giva$}{Mar 2022 - June 2022$}{Bangalore, India}
\begin{itemize}

\item Placeholder.
\item Placeholder.

\end{itemize}
\divider
\medskip
```