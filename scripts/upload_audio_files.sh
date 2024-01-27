for file in audio/*.webm; do
  filename=$(basename "$file")
  if aws s3 ls "s3://comme-un-poisson-dans-l-eau/$filename" 2>&1 | grep -q "$filename"; then
    echo "File $filename already exists on the bucket. Skipping..."
  else
    aws s3 cp "$file" s3://comme-un-poisson-dans-l-eau/ \
    --storage-class ONEZONE_IA \
    --acl public-read
  fi
done
