
<# AD���[�U�[�o�^����
�@�@�g�����F
�@�@  1.�ǉ�����AD���[�U�[��CSV�`���Ńe�L�X�g�ۑ�����B
     2.CSV �t�@�C���͖{Powershell�X�N���v�g�Ɠ���̃f�B���N�g���Ɋi�[����B
     3.AD�T�[�o�[��Ŗ{�X�N���v�g�Ŏ��s����B
     ���{�X�N���v�g�ł�CSV�t�@�C���̃G���[�`�F�b�N�͍s���Ă���܂���B
   �@  ����ȃt�H�[�}�b�g�ŋL�ڂ���Ă���CSV��O��Ƃ��Ă���܂��B
   �쐬�����F2018/05/17
   �X�V�����F
   �X�V�����F
   Ver.1.0.0
#>

New-EventLog -LogName Application -Source ADUserManagemnt
Write-EventLog -LogName Application -EntryType Info -Source ADUserManagemnt -EventId 100 -Message "AD���[�U�[�o�^�������J�n���܂��B"

$domain=Get-ADDomain;
try {
    import-csv -Encoding Default addAduser.csv | Foreach-Object {
        $args = @{
            Path=$_."OU"
            SamAccountName=$_."���[�UID"
            UserPrincipalName=$_."���[�UID" + "@" + $domain.DNSRoot
            AccountPassword=ConvertTo-SecureString -AsPlainText $_."�p�X���[�h" -force
            Name=$_."���O"
            Surname=$_."��"
            GivenName=$_."��"
            DisplayName=$_."���O"
            ProfilePath=$_."�ړ��v���t�@�C��"
            Enabled=$True
        };
        
        New-ADUser @args;
        $groups=$_."�O���[�v" -split ",";
        foreach($i in $groups){
            Add-ADGroupMember $i $_."���[�UID"
        }
    }
}catch{
    Write-EventLog -LogName Application -EntryType Info -Source ADUserManagemnt -EventId 1 -Message "AD���[�U�[�o�^�����ŃG���[���������܂����B"
}finally{
    Write-EventLog -LogName Application -EntryType Info -Source ADUserManagemnt -EventId 101 -Message "AD���[�U�[�o�^�������I�����܂��B"
}
