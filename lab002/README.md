## Transformer Encoder (3 Layers, 4 Attention Heads each)

```mermaid
flowchart TD

%% Input
A[Input Embeddings + Positional Encoding]

%% Layer 1
subgraph L1["Encoder Layer 1"]
    subgraph H1["Multi-Head Self-Attention"]
        H1a[Head 1]
        H1b[Head 2]
        H1c[Head 3]
        H1d[Head 4]
    end
    Hcat1[Concatenate Heads]
    Hlin1[Linear Projection W^O]
    R1[Residual Connection]
    N1[Layer Normalization]
    F1[Feed-Forward Network]
    R1b[Residual Connection]
    N1b[Layer Normalization]
end

%% Layer 2
subgraph L2["Encoder Layer 2"]
    subgraph H2["Multi-Head Self-Attention"]
        H2a[Head 1]
        H2b[Head 2]
        H2c[Head 3]
        H2d[Head 4]
    end
    Hcat2[Concatenate Heads]
    Hlin2[Linear Projection W^O]
    R2[Residual Connection]
    N2[Layer Normalization]
    F2[Feed-Forward Network]
    R2b[Residual Connection]
    N2b[Layer Normalization]
end

%% Layer 3
subgraph L3["Encoder Layer 3"]
    subgraph H3["Multi-Head Self-Attention"]
        H3a[Head 1]
        H3b[Head 2]
        H3c[Head 3]
        H3d[Head 4]
    end
    Hcat3[Concatenate Heads]
    Hlin3[Linear Projection W^O]
    R3[Residual Connection]
    N3[Layer Normalization]
    F3[Feed-Forward Network]
    R3b[Residual Connection]
    N3b[Layer Normalization]
end

%% Connections
A --> L1
N1b --> L2
N2b --> L3
N3b --> Z[Final Contextualized Representations]
