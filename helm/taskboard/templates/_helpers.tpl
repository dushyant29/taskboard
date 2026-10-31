{{- define "tb.labels" -}}
app.kubernetes.io/part-of: taskboard
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
{{- define "tb.dburl" -}}
{{- if .Values.postgres.enabled -}}
postgresql+psycopg2://{{ .Values.postgres.user }}:{{ .Values.postgres.password }}@{{ .Release.Name }}-postgres:5432/{{ .Values.postgres.db }}
{{- else -}}{{ required "externalDatabaseUrl required" .Values.externalDatabaseUrl }}{{- end -}}
{{- end }}
