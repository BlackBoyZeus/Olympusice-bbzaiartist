# Music Generator Bundle in S3

The bundle file has been split into parts and uploaded to Amazon S3. You can download and reassemble it using the following links.

## Quick Download

Use this script to download and reassemble the bundle in one step:

[Download and Reassemble Script](https://bbzaiartiste.s3.amazonaws.com/music-generator-bundle/download_and_reassemble.sh?AWSAccessKeyId=AKIAWXU463JZC56KVAW3&Signature=BVYTiHiGpd9HaFR5InqCedkXUkc%3D&Expires=1749871886)

```bash
# Download the script
curl -o download_and_reassemble.sh "https://bbzaiartiste.s3.amazonaws.com/music-generator-bundle/download_and_reassemble.sh?AWSAccessKeyId=AKIAWXU463JZC56KVAW3&Signature=BVYTiHiGpd9HaFR5InqCedkXUkc%3D&Expires=1749871886"

# Make it executable
chmod +x download_and_reassemble.sh

# Run it
./download_and_reassemble.sh
```

## Manual Download

If you prefer to download the parts manually, use these links:

1. [bundle-part-aa](https://bbzaiartiste.s3.amazonaws.com/music-generator-bundle/bundle-part-aa?AWSAccessKeyId=AKIAWXU463JZC56KVAW3&Signature=g6C3dohRl8TGayRQW8vFqOYuZIw%3D&Expires=1749871840)
2. [bundle-part-ab](https://bbzaiartiste.s3.amazonaws.com/music-generator-bundle/bundle-part-ab?AWSAccessKeyId=AKIAWXU463JZC56KVAW3&Signature=g%2FmS%2F0zm937guK527Ap429BUrNM%3D&Expires=1749871841)
3. [bundle-part-ac](https://bbzaiartiste.s3.amazonaws.com/music-generator-bundle/bundle-part-ac?AWSAccessKeyId=AKIAWXU463JZC56KVAW3&Signature=a8oxFd2l7JyEdqQOCy8fbpoFpfg%3D&Expires=1749871841)
4. [README.md](https://bbzaiartiste.s3.amazonaws.com/music-generator-bundle/README.md?AWSAccessKeyId=AKIAWXU463JZC56KVAW3&Signature=4daWNmwSHemyqHrU1d3Y%2BtyR54Y%3D&Expires=1749871851)
5. [reassemble.sh](https://bbzaiartiste.s3.amazonaws.com/music-generator-bundle/reassemble.sh?AWSAccessKeyId=AKIAWXU463JZC56KVAW3&Signature=SjGdpYSdvw8w0LNcjCes4cqhVSQ%3D&Expires=1749871851)

After downloading all parts, reassemble the bundle with:

```bash
cat bundle-part-* > music-generator-bundle-with-madison-june.bundle
```

## Note

These links will expire in 7 days (on June 13, 2025). If you need access after that date, new presigned URLs will need to be generated.

## Using the Bundle

After reassembling the bundle:

1. Clone the repository from AWS CodeCommit:
   ```bash
   git clone ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/music-generator
   cd music-generator
   ```

2. Unbundle the bundle file:
   ```bash
   git bundle unbundle /path/to/music-generator-bundle-with-madison-june.bundle
   ```

3. Check out the madison-june-update branch:
   ```bash
   git checkout madison-june-update
   ```

