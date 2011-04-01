unit main;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, CheckLst, MPlayer, Buttons, ExtCtrls, ACS_Classes,
  ACS_DXAudio, ACS_smpeg, ACS_WinMedia, ComCtrls;

type
  TForm1 = class(TForm)
    GroupBox1: TGroupBox;
    CheckBox1: TCheckBox;
    CheckBox2: TCheckBox;
    CheckBox3: TCheckBox;
    CheckBox16: TCheckBox;
    CheckBox17: TCheckBox;
    CheckBox18: TCheckBox;
    GroupBox2: TGroupBox;
    CheckBox4: TCheckBox;
    CheckBox5: TCheckBox;
    CheckBox6: TCheckBox;
    CheckBox19: TCheckBox;
    CheckBox20: TCheckBox;
    CheckBox21: TCheckBox;
    GroupBox3: TGroupBox;
    CheckBox7: TCheckBox;
    CheckBox8: TCheckBox;
    CheckBox9: TCheckBox;
    CheckBox22: TCheckBox;
    CheckBox23: TCheckBox;
    CheckBox24: TCheckBox;
    CheckBox14: TCheckBox;
    GroupBox4: TGroupBox;
    CheckBox10: TCheckBox;
    CheckBox11: TCheckBox;
    CheckBox12: TCheckBox;
    CheckBox13: TCheckBox;
    CheckBox15: TCheckBox;
    CheckBox25: TCheckBox;
    CheckBox26: TCheckBox;
    CheckBox27: TCheckBox;
    CheckBox28: TCheckBox;
    Button1: TButton;
    Button2: TButton;
    Button3: TButton;
    BitBtn1: TBitBtn;
    Panel1: TPanel;
    MP3In1: TMP3In;
    DXAudioOut1: TDXAudioOut;
    Button4: TButton;
    TrackBar1: TTrackBar;
    Label1: TLabel;
    Label2: TLabel;
    Label3: TLabel;
    TrackBar2: TTrackBar;
    Label4: TLabel;
    Label5: TLabel;
    Label6: TLabel;
    Label7: TLabel;
    Label8: TLabel;
    Label9: TLabel;
    TrackBar3: TTrackBar;
    TrackBar4: TTrackBar;
    Button5: TButton;
    procedure Button1Click(Sender: TObject);
    procedure Button2Click(Sender: TObject);
    procedure Button3Click(Sender: TObject);
    procedure Button4Click(Sender: TObject);
    procedure BitBtn1Click(Sender: TObject);
    procedure TrackBar1Change(Sender: TObject);
    procedure TrackBar2Change(Sender: TObject);
    procedure TrackBar3Change(Sender: TObject);
    procedure TrackBar4Change(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure Button5Click(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

const maxsounds=10;
ModeStr: array[TMPModes] of string = ('Not ready', 'Stopped', 'Playing', 'Recording', 'Seeking', 'Paused', 'Open');

var
  Form1: TForm1;
  playing: boolean=false;
  THHandle: THandle;
  THID: Cardinal;
  last_player_used:byte=0;
  next_spell:string;
  queue:byte=0;

implementation

{$R *.dfm}


function get_next_spell: string;
var i: byte;
cb: TCheckBox;
begin

  cb:=tCheckBox.Create(Form1);
  repeat
        i:=random(Form1.ComponentCount);
        Application.ProcessMessages;
        if (Form1.Components[i] is TCheckBox) and (Form1.Components[i].tag>=0)
                then cb:=Form1.Components[i] as TCheckBox
        else continue;
  until cb.Checked;
  result:=cb.Caption;
end;

function get_next_file(spell: string):string;
var s:string; i:byte;
begin
   while pos(' ',spell)>0 do
    delete(spell, pos(' ',spell),1);
  repeat
    i:=random(maxsounds);
    s:=extractfilepath(application.ExeName)+'sounds\'+spell+inttostr(i)+'.mp3';
  until fileexists(s);
  result:=s;
end;

procedure reclick(tag1, tag2: integer);
var i, s0, s1: integer; make: boolean;
begin
   s0:=0; s1:=0;
   for i:=0 to Form1.ComponentCount-1 do
   if (Form1.Components[i].Tag in [tag1, tag2])
   and (Form1.Components[i] is TCheckBox)
   then
        if (Form1.components[i] as tcheckbox).Checked
        then inc(s1)
        else inc(s0);
   make:=s0>s1; // Если сброшенных больше, чем установленных - будем устанавливать
   for i:=0 to Form1.ComponentCount-1 do
   if (Form1.Components[i].Tag in [tag1, tag2])
   and (Form1.Components[i] is TCheckBox)
   then (Form1.components[i] as tcheckbox).Checked:=make;
end;

procedure TForm1.Button1Click(Sender: TObject);
begin
  reclick(0,1);

end;

procedure TForm1.Button2Click(Sender: TObject);
begin
 reclick(2,3);
end;

procedure TForm1.Button3Click(Sender: TObject);
begin
  reclick(1,3);
end;

procedure play_spell;
var spell_name, spell_file:string;
begin
   if Form1.DXAudioOut1.Status = tosPlaying then exit;
   spell_name:=get_next_spell;//showmessage(s);
   Form1.Panel1.Caption:=spell_name;
   application.processmessages;
   spell_file:=get_next_file(spell_name);
   Form1.mp3in1.filename:=spell_file;
   Form1.dxaudioout1.Run;
   repeat until Form1.DXAudioOut1.Status<>tosPlaying;
   //Реализуем задержку.
   if (pos('Maxima', spell_name)>0)
   or (spell_name='Expellearmus')
   or (spell_name='Petrificus Totalus')
     then
       sleep(Form1.trackbar2.position*100)
     else
       sleep(Form1.trackbar1.position*100);

   inc(queue);
   if queue>=FOrm1.trackbar3.position
   then begin
      sleep(Form1.TrackBar4.Position*1000);
      queue:=0;
   end;
end;


procedure TForm1.Button4Click(Sender: TObject);
begin
  if Form1.DXAudioOut1.Status = tosPlaying then exit;
  play_spell;
end;

procedure TForm1.BitBtn1Click(Sender: TObject);
var i:byte;
begin
playing:=not playing;
if playing then
begin
  BitBtn1.Kind:=bkNo;
  BitBtn1.Caption:='Стоп!';
end
else
begin
  BitBtn1.Kind:=bkAll;
  BitBtn1.Caption:='Понеслась!';
  queue:=0;
end;
  while playing do
    play_spell;
end;

procedure TForm1.TrackBar1Change(Sender: TObject);
begin
  label2.Caption:=Format('%3.1f', [TrackBar1.Position/10]);
end;

procedure TForm1.TrackBar2Change(Sender: TObject);
begin
  label4.Caption:=Format('%3.1f', [TrackBar2.Position/10]);
end;

procedure TForm1.TrackBar3Change(Sender: TObject);
begin
  label6.Caption:=inttostr(TrackBar3.Position);
end;

procedure TForm1.TrackBar4Change(Sender: TObject);
begin
   label8.Caption:=inttostr(TrackBar4.Position);
end;

procedure TForm1.FormCreate(Sender: TObject);
begin
  randomize;
end;

procedure TForm1.Button5Click(Sender: TObject);
begin
  showmessage('Программа для тренировки чар и щитов для ролевой игры "Хогвартские Сезоны"'+#13+#10+
  'Что такое Хогвартские Сезоны - http://hp-ekb.ru'+#13+#10+
  'Что такое чары и щиты - http://hp-ekb.ru/game_cast.php'+#13+#10+
  'Как это все должно выглядеть - http://community.livejournal.com/hp_ekb/597336.html'+#13+#10+
  'Кто виноват в данном конкретном проявлении поттеротолчкизма - я, Хыиуду, широко известный в узких кругах как Кейси МакНелли.'+#13+#10+
  'Дисклеймеры и прочие копирадости: все права мои, ни на что не претендую, копирование, распространение и использование свободное и бесплатное'+#13+#10+
  'Повторяю печатными русскими буквами: программа БЕСПЛАТНАЯ, ясно, солнышко?');
end;

end.
