# GitHub 푸시 간편 실행 스크립트
param (
    [string]$RepoUrl = ""
)

Write-Host "=== TaskPulse (TTA_260908) GitHub 푸시 시작 ===" -ForegroundColor Cyan

# 1. Git 사용자 정보 확인 및 입력
$currentName = git config user.name
$currentEmail = git config user.email

if (-not $currentName) {
    $name = Read-Host "GitHub 사용자 이름 (또는 닉네임) 입력"
    git config user.name "$name"
}

if (-not $currentEmail) {
    $email = Read-Host "GitHub 계정 이메일 입력"
    git config user.email "$email"
}

# 2. 파일 추가 및 커밋
git add .
git commit -m "feat: TaskPulse To-Do Web App (TTA_260908)"

# 3. 기본 브랜치를 main으로 설정
git branch -M main

# 4. 원격 저장소 URL 연결
if (-not $RepoUrl) {
    Write-Host ""
    Write-Host "GitHub(https://github.com/new)에서 생성한 레포지토리 URL을 입력하세요." -ForegroundColor Yellow
    Write-Host "예시: https://github.com/당신의계정/TTA_260908.git" -ForegroundColor Gray
    $RepoUrl = Read-Host "레포지토리 URL"
}

if ($RepoUrl) {
    git remote remove origin 2>$null
    git remote add origin $RepoUrl
    Write-Host "원격 저장소 '$RepoUrl'로 푸시 중..." -ForegroundColor Green
    git push -u origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Host "🎉 GitHub 업로드가 성공적으로 완료되었습니다!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 푸시 중 오류가 발생했습니다. 권한 및 URL을 확인해주세요." -ForegroundColor Red
    }
} else {
    Write-Host "❌ URL이 입력되지 않아 푸시를 건너뜁니다." -ForegroundColor Red
}
