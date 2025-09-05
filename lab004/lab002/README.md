```mermaid
flowchart TD

%% Input
A[Input Embeddings + Positional Encoding]

%% Layer 1
subgraph L1[Encoder Layer 1]
    subgraph H1[Multi-Head Self-Attention (4 heads)]
        H1a[Head 1]
        H1b[Head 2]
        H1c[Head 3]
        H1d[Head 4]
    end
    Hcat1[Concatenate Heads]
    Hlin1[Linear Projection W^O]
    F1[Feed-Forward Network]
end

%% Layer 2
subgraph L2[Encoder Layer 2]
    subgraph H2[Multi-Head Self-Attention (4 heads)]
        H2a[Head 1]
        H2b[Head 2]
        H2c[Head 3]
        H2d[Head 4]
    end
    Hcat2[Concatenate Heads]
    Hlin2[Linear Projection W^O]
    F2[Feed-Forward Network]
end

%% Layer 3
subgraph L3[Encoder Layer 3]
    subgraph H3[Multi-Head Self-Attention (4 heads)]
        H3a[Head 1]
        H3b[Head 2]
        H3c[Head 3]
        H3d[Head 4]
    end
    Hcat3[Concatenate Heads]
    Hlin3[Linear Projection W^O]
    F3[Feed-Forward Network]
end

%% Connections
A --> L1
F1 --> L2
F2 --> L3
F3 --> Z[Final Contextualized Representations]
```
