# Status update templates

Copy, fill in, post. Keep the same format for every update so readers can
scan them quickly.

## Internal update (incident channel)

```
[SEV<N>] <service>: <one-line impact>
Status:      Investigating | Mitigating | Monitoring | Resolved
Impact:      <who is affected and how, with numbers if known>
Actions:     <what was done since the last update>
Next step:   <what happens next and who owns it>
IC:          <name>
Next update: <hh:mm UTC>
```

## Customer-facing update (status page)

**Investigating**

> We are investigating reports of `<errors / slow responses>` when
> `<customers do X>`. We will provide an update by `<hh:mm UTC>`.

**Identified / mitigating**

> We have identified the cause of `<symptom>` and are applying a fix. Some
> customers may continue to see `<symptom>` until it is complete. Next update
> by `<hh:mm UTC>`.

**Monitoring**

> A fix has been applied and `<feature>` is working normally. We are
> monitoring to confirm full recovery. Next update by `<hh:mm UTC>`.

**Resolved**

> Between `<hh:mm>` and `<hh:mm UTC>` on `<date>`, some customers experienced
> `<symptom>`. The issue has been resolved. `<No data was lost.>` We will
> publish a summary of what happened and the steps we are taking to prevent
> it.

## Writing guidelines

- Lead with user impact, not internal component names.
- Do not guess at causes in public updates.
- Always give the time of the next update, and post it on time even if
  nothing has changed.
