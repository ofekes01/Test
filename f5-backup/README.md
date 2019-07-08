```

Apply the job

```bash
 splatt helm delete --purge  f5-backup
 splatt apply chart charts/optional/f5-backup
```

To check the logs:

```bash
POD_NAME=$(splatt kubectl -n kube-system get pod -o=jsonpath="{..metadata.name}" -l job-name=f5-backup)
splatt kubectl -n kube-system log -f  $POD_NAME
```

