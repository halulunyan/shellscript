
<# ADユーザー登録処理
　　使い方：
　　  1.追加するADユーザーをCSV形式でテキスト保存する。
     2.CSV ファイルは本Powershellスクリプトと同一のディレクトリに格納する。
     3.ADサーバー上で本スクリプトで実行する。
     ※本スクリプトではCSVファイルのエラーチェックは行っておりません。
   　  正常なフォーマットで記載されているCSVを前提としております。
   作成日時：2018/05/17
   更新日時：
   更新履歴：
   Ver.1.0.0
#>

New-EventLog -LogName Application -Source ADUserManagemnt
Write-EventLog -LogName Application -EntryType Info -Source ADUserManagemnt -EventId 100 -Message "ADユーザー登録処理を開始します。"

$domain=Get-ADDomain;
try {
    import-csv -Encoding Default addAduser.csv | Foreach-Object {
        $args = @{
            Path=$_."OU"
            SamAccountName=$_."ユーザID"
            UserPrincipalName=$_."ユーザID" + "@" + $domain.DNSRoot
            AccountPassword=ConvertTo-SecureString -AsPlainText $_."パスワード" -force
            Name=$_."名前"
            Surname=$_."姓"
            GivenName=$_."名"
            DisplayName=$_."名前"
            ProfilePath=$_."移動プロファイル"
            Enabled=$True
        };
        
        New-ADUser @args;
        $groups=$_."グループ" -split ",";
        foreach($i in $groups){
            Add-ADGroupMember $i $_."ユーザID"
        }
    }
}catch{
    Write-EventLog -LogName Application -EntryType Info -Source ADUserManagemnt -EventId 1 -Message "ADユーザー登録処理でエラーが発生しました。"
}finally{
    Write-EventLog -LogName Application -EntryType Info -Source ADUserManagemnt -EventId 101 -Message "ADユーザー登録処理を終了します。"
}
