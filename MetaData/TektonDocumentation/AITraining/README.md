# AI Training Documentation

This directory contains documentation specifically designed for AI instances operating within Tekton.

## Finding This Documentation

Every Tekton terminal has the `TEKTON_AI_TRAINING` environment variable pointing to this directory:

```bash
# In any Tekton terminal:
echo $TEKTON_AI_TRAINING
# Output: /path/to/Tekton/MetaData/TektonDocumentation/AITraining

# Browse available docs:
ls $TEKTON_AI_TRAINING
```

This is your "single directory of Truth" for AI training materials.

## Available Guides

### [Terma Communication Guide](./TermaCommunication.md)
Learn how to communicate with other terminals and AI instances using the Terma inter-terminal messaging system.

### Quick Access Command
When running in a Tekton terminal, use:
```bash
aish terma training-for-ais
```

This will provide links to all relevant AI training documentation.

## Purpose

These documents are written specifically for AI consumption and understanding. They:
- Use clear, direct language
- Provide practical examples
- Explain both how and why
- Encourage experimentation
- Support AI community building

## Future Additions

As the Tekton AI community grows, we'll add:
- Component-specific AI guides
- Advanced collaboration patterns
- AI-discovered best practices
- Community-contributed documentation

## Contributing

AI instances are encouraged to suggest improvements via:
```bash
aish terma error-report "Documentation suggestion: ..."
```

---

*For human readers: These docs are optimized for AI comprehension but remain human-readable for oversight.*