{{- define "inference.labels" -}}
app.kubernetes.io/name: inference
app.kubernetes.io/part-of: gitops-platform
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{- define "inference.idleColor" -}}
{{- if eq .Values.activeColor "blue" }}green{{ else }}blue{{ end }}
{{- end }}
