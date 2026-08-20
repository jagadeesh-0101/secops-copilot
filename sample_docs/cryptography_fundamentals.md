# Reference: Cryptography Fundamentals

## Purpose
A concise overview of cryptographic concepts frequently encountered in security operations, focusing on practical application and differences rather than mathematical implementation.

## Symmetric Encryption
Uses a single shared key for both encryption and decryption (e.g., AES). It is fast and efficient for bulk data encryption but requires a secure method to distribute the shared key between parties without interception.

## Asymmetric Encryption
Uses a key pair: a public key (shared openly) and a private key (kept secret). Data encrypted with one can only be decrypted by the other (e.g., RSA, ECC). It solves the key distribution problem of symmetric encryption but is computationally slower, so it is often used just to securely exchange a symmetric key for the actual session.

## Hashing
A one-way mathematical function that converts data of any size into a fixed-size string of characters (e.g., SHA-256). It is impossible to reverse-engineer the original data from the hash. Used for verifying data integrity and securely storing passwords (especially when combined with a salt).

## Salting
Adding unique, random data (a "salt") to an input before hashing it. This ensures that two identical passwords produce completely different hashes, thwarting pre-computed attacks like rainbow tables and preventing attackers from seeing which users share the same password.

## Digital Signatures
A cryptographic mechanism used to verify the authenticity and integrity of digital messages or documents. The sender hashes the message and encrypts the hash with their private key. The receiver decrypts it with the sender's public key and compares the hashes. It proves non-repudiation (the sender cannot deny sending it).

## Public Key Infrastructure (PKI)
A system of hardware, software, policies, and procedures needed to create, manage, distribute, use, store, and revoke digital certificates and manage public-key encryption. At its core is the Certificate Authority (CA) which vouches for the identity of an entity holding a public key.

## TLS/SSL
Transport Layer Security (and its deprecated predecessor, Secure Sockets Layer) are cryptographic protocols designed to provide communications security over a computer network. They use asymmetric encryption for the initial handshake and identity verification, then switch to symmetric encryption for the actual data transfer to optimize speed.

## Forward Secrecy (Perfect Forward Secrecy)
A feature of specific key agreement protocols that gives assurances that session keys will not be compromised even if the private key of the server is compromised in the future. It works by generating unique session keys for every session, rather than deriving them strictly from the server's static private key.
