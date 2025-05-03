# Welcome to Agentics-Labs Training

**Agentics-Labs** is an advanced, hands-on training experience for those who want to go beyond the hype and dive deep into the **foundations of agentic AI**. Whether you're a **DevOps engineer**, **ethical hacker**, **network specialist**, **pen-tester**, or **developer**, this course is your gateway to mastering the **low-level internals** of the OpenAI ecosystem.

## 🔍 What You'll Learn

- How to work directly with the **OpenAI API Chat completion**, the brand new **OpenAI responses API** and the new **OpenAI Agents SDK**
- How to build and chain intelligent agents using **LangChain** and custom tools
- The core principles behind **agentic systems** that plan, reason, and act
- How to integrate AI agents into real-world workflows for **security**, **automation**, and **development**
- How to debug AI agents using **MITM proxy** and **tracing**
- Security pitfalls and hacking challenges
  
This is more than just a workshop, it's an exploration of how intelligent agents are transforming the way we build and secure systems.
By the end, you'll not only know how to use AI—you'll know how to *engineer* it.
Let’s plug in, patch deep, and push the boundaries of what’s possible.

Welcome to the lab and let's **#HACKTOLEARN** 🚀

## 🔐 Getting Access to the Lab via SSH

Each lab student has access to a virtual machine, accessible over SSH. Use the credentials provided to you and use the following pattern to connect:

```bash
ssh -i lab.pem -L 8080:localhost:8080 -L 8081:localhost:8081 ubuntu@studentXX.labs.kubiosec.tech
# Replace XX with your student number, e.g., 01, 02, ..., 11
```

## 🧪 Lab Overview

Each lab is structured to gradually build your understanding and capabilities, from basic API calls to full agent orchestration and security integration.

| Lab | Focus Area                                      | Tools & Topics                              |
|-----|-------------------------------------------------|---------------------------------------------|
| [lab01](./lab01) | OpenAI - Chat completions basics              | curl, few-shot prompts, image analysis     |
| [lab02](./lab02) | OpenAI - Responses API basics                     | curl, tools, structured output                     |
| [lab03](./lab03) | Model evaluation                                | curl       |
| [lab04](./lab04) | RAG                                             | python, RAG, chroma, llama-index                |
| [lab05](./lab05) | Tools                                           | python, langchain,                       |
| [lab06](./lab06) | xxxxxx                          | Planning, reactive vs. deliberative agents  |
| [lab07](./lab07) | xxxxxxx                 | Rate-limiting, auth, API wrappers           |
| [lab08](./lab08) | xxxxxxx      | Shell tool, command validation              |
| [lab09](./lab09) | xxxxxxx            | Toolkits, intermediate reasoning            |
| [lab10](./lab10) | xxxxxxx               | Success metrics, reward shaping             |
| [lab11](./lab11) | xxxxxxx      | Messaging, task splitting, autonomy levels  |

Each labs has a different environment, feel free to fork, hack, and explore beyond the tasks!

